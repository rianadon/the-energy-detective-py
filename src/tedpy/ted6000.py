import asyncio

from .ted import *

ENDPOINT_URL_SETTINGS = "http://{}/api/SystemSettings.xml"
ENDPOINT_URL_DASHBOARD = "http://{}/api/DashData.xml?T=0&D=0&M=0"
ENDPOINT_URL_MTU = "http://{}/api/SystemOverview.xml?T=0&D=0&M=0"
ENDPOINT_URL_SPYDER = "http://{}/api/SpyderData.xml?T=0&M=0&D=0"


class TED6000(TED):
    """Instance of TED6000"""

    def __init__(self, host, async_client=None):
        super().__init__(host, async_client)

        self.endpoint_settings_results = None
        self.endpoint_dashboard_results = None
        self.endpoint_mtu_results = None
        self.endpoint_spyder_results = None

    async def update(self):
        """Fetch data from the endpoints."""
        await asyncio.gather(
            self._update_endpoint("endpoint_settings_results", ENDPOINT_URL_SETTINGS),
            self._update_endpoint("endpoint_dashboard_results", ENDPOINT_URL_DASHBOARD),
            self._update_endpoint("endpoint_mtu_results", ENDPOINT_URL_MTU),
            self._update_endpoint("endpoint_spyder_results", ENDPOINT_URL_SPYDER),
        )

        self._parse_mtus()
        self._parse_spyders()

    async def check(self):
        """Check if the required endpoint are accessible."""
        return await self._check_endpooint(ENDPOINT_URL_SETTINGS)

    @property
    def gateway_id(self):
        """Return the id / serial number for the gateway."""
        return self.endpoint_settings_results["SystemSettings"]["Gateway"]["GatewayID"]

    @property
    def gateway_description(self):
        """Return the description for the gateway."""
        return self.endpoint_settings_results["SystemSettings"]["Gateway"][
            "GatewayDescription"
        ]

    @property
    def system_type(self):
        """Return the system type, represented by a number."""
        return self.endpoint_settings_results["SystemSettings"]["Configuration"][
            "SystemType"
        ]

    @property
    def num_mtus(self):
        """Return the number of MTUs."""
        return self.endpoint_settings_results["SystemSettings"]["NumberMTU"]

    @property
    def polling_delay(self):
        """Return the delay between successive polls of MTU data."""
        return self.endpoint_settings_results["SystemSettings"]["MTUPollingDelay"]

    def total_consumption(self):
        """Return consumption information for the whole system."""
        data = self.endpoint_dashboard_results["DashData"]
        return Consumption(int(data["Now"]), int(data["TDY"]), int(data["MTD"]))

    def mtu_consumption(self, mtu):
        """Return consumption information for a MTU."""
        mtu_doc = self.endpoint_mtu_results["DialDataDetail"]["MTUVal"][
            "MTU%d" % mtu.position
        ]
        value = int(mtu_doc["Value"])
        ap_power = int(mtu_doc["KVA"])
        power_factor = int(mtu_doc["PF"])
        voltage = int(mtu_doc["Voltage"]) / 10
        return MtuConsumption(value, ap_power, power_factor, voltage)

    def spyder_ctgroup_consumption(self, spyder, ctgroup):
        """Return consumption information for a spyder ctgroup."""
        group_doc = self.endpoint_spyder_results["SpyderData"]["Spyder"][
            spyder.position
        ]["Group"][ctgroup.position]
        return Consumption(
            int(group_doc["Now"]), int(group_doc["TDY"]), int(group_doc["MTD"])
        )

    def _parse_mtus(self):
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []
        mtu_settings = self.endpoint_settings_results["SystemSettings"]["MTUs"]["MTU"]
        config_settings = self.endpoint_settings_results["SystemSettings"][
            "Configuration"
        ]

        for mtu_doc in mtu_settings:
            mtu_id = mtu_doc["MTUID"]
            mtu_number = int(mtu_doc["MTUNumber"])
            if mtu_id != "000000":
                mtu = TedMtu(
                    mtu_id,
                    mtu_number,
                    mtu_doc["MTUDescription"],
                    config_settings["MTUType%d" % mtu_number],
                    int(mtu_doc["PowerCalibrationFactor"]),
                    int(mtu_doc["VoltageCalibrationFactor"]),
                )
                self.mtus.append(mtu)

    def _parse_spyders(self):
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
