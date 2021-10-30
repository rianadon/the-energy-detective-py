"""Implementation for the TED6000 meter."""
import asyncio
from typing import Any

import httpx

from .dataclasses import (
    Consumption,
    MtuNet,
    MtuType,
    TedCt,
    TedCtGroup,
    TedMtu,
    TedSpyder,
)
from .ted import TED

ENDPOINT_URL_SETTINGS = "http://{}/api/SystemSettings.xml"
ENDPOINT_URL_DASHBOARD = "http://{}/api/DashData.xml?T=0&D=0&M=0"
ENDPOINT_URL_MTUDASHBOARD = "http://{}/api/DashData.xml?T=0&D=255&M={}"
ENDPOINT_URL_MTU = "http://{}/api/SystemOverview.xml?T=0&D=0&M=0"
ENDPOINT_URL_SPYDER = "http://{}/api/SpyderData.xml?T=0&M=0&D=0"


class TED6000(TED):
    """Instance of TED6000."""

    def __init__(self, host: str, async_client: httpx.AsyncClient = None) -> None:
        super().__init__(host, async_client)

        self.endpoint_settings_results: Any = None
        self.endpoint_dashboard_results: Any = None
        self.endpoint_mtu1_dashboard_results: Any = None
        self.endpoint_mtu2_dashboard_results: Any = None
        self.endpoint_mtu3_dashboard_results: Any = None
        self.endpoint_mtu4_dashboard_results: Any = None
        self.endpoint_mtu_results: Any = None
        self.endpoint_spyder_results: Any = None

    async def update(self) -> None:
        """Fetch settings data from the endpoints."""
        await asyncio.gather(
            self._update_endpoint("endpoint_settings_results", ENDPOINT_URL_SETTINGS),
        )

        self._parse_mtus()

        """Fetch MTU/Spyder data results"""
        await asyncio.gather(
            self._update_endpoint("endpoint_dashboard_results", ENDPOINT_URL_DASHBOARD),
            self._update_endpoint("endpoint_mtu_results", ENDPOINT_URL_MTU),
            self._update_endpoint("endpoint_spyder_results", ENDPOINT_URL_SPYDER),
            *map(lambda mtu: self._update_endpoint(
                "endpoint_mtu%d_dashboard_results" % mtu.position, 
                ENDPOINT_URL_MTUDASHBOARD, str(mtu.position)), self.mtus)
        )

        self._parse_spyders()

    async def check(self) -> bool:
        """Check if the required endpoint are accessible."""
        return await self._check_endpoint(ENDPOINT_URL_SETTINGS)

    @property
    def gateway_id(self) -> str:
        """Return the id / serial number for the gateway."""
        return self.endpoint_settings_results["SystemSettings"]["Gateway"]["GatewayID"]

    @property
    def gateway_description(self) -> str:
        """Return the description for the gateway."""
        return self.endpoint_settings_results["SystemSettings"]["Gateway"][
            "GatewayDescription"
        ]

    @property
    def polling_delay(self) -> int:
        """Return the delay between successive polls of MTU data."""
        return self.endpoint_settings_results["SystemSettings"]["MTUPollingDelay"]

    def total_consumption(self) -> Consumption:
        """Return consumption information for the whole system."""
        data = self.endpoint_dashboard_results["DashData"]
        return Consumption(int(data["Now"]), int(data["TDY"]), int(data["MTD"]))

    def mtu_value(self, mtu: TedMtu) -> MtuNet:
        """Return consumption or production information for a MTU based on type."""
        mtu_doc = self.endpoint_mtu_results["DialDataDetail"]["MTUVal"][
            "MTU%d" % mtu.position
        ]
        type = mtu.type
        dashdata = getattr(self, "endpoint_mtu%d_dashboard_results" % mtu.position)["DashData"]
        now = int(dashdata["Now"])
        tdy = int(dashdata["TDY"])
        mtd = int(dashdata["MTD"])
        ap_power = int(mtu_doc["KVA"])
        power_factor = int(mtu_doc["PF"]) / 10
        voltage = int(mtu_doc["Voltage"]) / 10
        return MtuNet(type, now, tdy, mtd, ap_power, power_factor, voltage)

    def spyder_ctgroup_consumption(
        self, spyder: TedSpyder, ctgroup: TedCtGroup
    ) -> Consumption:
        """Return consumption information for a spyder ctgroup."""
        group_doc = self.endpoint_spyder_results["SpyderData"]["Spyder"][
            spyder.position
        ]["Group"][ctgroup.position]
        return Consumption(
            int(group_doc["Now"]), int(group_doc["TDY"]), int(group_doc["MTD"])
        )

    def _parse_mtu_type(self, mtu_type: int) -> MtuType:
        switcher = {
            0: MtuType.NET,
            1: MtuType.LOAD,
            2: MtuType.GENERATION,
            3: MtuType.STAND_ALONE,
        }
        return switcher.get(mtu_type, MtuType.STAND_ALONE)

    def _parse_mtus(self) -> None:
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []

        num_mtus = int(self.endpoint_settings_results["SystemSettings"]["NumberMTU"])
        mtu_settings = self.endpoint_settings_results["SystemSettings"]["MTUs"]["MTU"]
        config_settings = self.endpoint_settings_results["SystemSettings"][
            "Configuration"
        ]
        for mtu_doc in mtu_settings[0:num_mtus]:
            mtu_number = int(mtu_doc["MTUNumber"])
            mtu = TedMtu(
                mtu_doc["MTUID"],
                mtu_number,
                mtu_doc["MTUDescription"],
                self._parse_mtu_type(int(config_settings["MTUType%d" % mtu_number])),
                int(mtu_doc["PowerCalibrationFactor"]) / 10,
                int(mtu_doc["VoltageCalibrationFactor"]) / 10,
            )
            self.mtus.append(mtu)

    def _parse_spyders(self) -> None:
        """Fill the list of Spyders with Spyders parsed from the xml data."""
        self.spyders = []
        spyder_settings = self.endpoint_settings_results["SystemSettings"]["Spyders"][
            "Spyder"
        ]
        enabled_spyders = (s for s in spyder_settings if int(s["Enabled"]) == 1)

        for spyder_count, spyder_doc in enumerate(enabled_spyders):
            isSecondary = int(spyder_doc["Secondary"])
            if isSecondary == 0:
                spyder = TedSpyder(
                    spyder_count, isSecondary, self.mtus[spyder_count].id, []
                )
            else:
                spyder = TedSpyder(
                    spyder_count, isSecondary, self.mtus[spyder_count - 1].id, []
                )

            ct_list = [
                TedCt(i, doc["Description"], int(doc["Type"]), int(doc["Mult"]))
                for i, doc in enumerate(spyder_doc["CT"])
            ]

            used_groups = (g for g in spyder_doc["Group"] if int(g["UseCT"]) != 0)
            for ctgroup_count, group_doc in enumerate(used_groups):
                use_ct = int(group_doc["UseCT"])
                if use_ct != 0:
                    group_cts = []
                    for x in range(8):
                        if (use_ct >> x) & 1 == 1:
                            group_cts.append(ct_list[x])
                    spyder.ctgroups.append(
                        TedCtGroup(ctgroup_count, group_doc["Description"], group_cts)
                    )

            self.spyders.append(spyder)
