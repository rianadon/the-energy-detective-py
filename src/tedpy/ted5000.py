"""Implementation for the TED5000 meter."""
import asyncio
from typing import Any

import httpx

from .dataclasses import EnergyYield, MtuType, Power, TedMtu
from .ted import TED

ENDPOINT_URL_SETTINGS = "http://{}/api/SystemSettings.xml"
ENDPOINT_URL_DATA = "http://{}/api/LiveData.xml"


class TED5000(TED):
    """Instance of TED5000."""

    def __init__(self, host: str, async_client: httpx.AsyncClient = None):
        """Init the TED5000."""
        super().__init__(host, async_client)

        self.endpoint_settings_results: Any = None
        self.endpoint_data_results: Any = None

    async def update(self) -> None:
        """Fetch data from the endpoints."""
        await asyncio.gather(
            self._update_endpoint("endpoint_settings_results", ENDPOINT_URL_SETTINGS),
            self._update_endpoint("endpoint_data_results", ENDPOINT_URL_DATA),
        )

        self._parse_mtus()

    async def check(self) -> bool:
        """Check if the required endpoint are accessible."""
        return await self._check_endpoint(ENDPOINT_URL_DATA)

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

    def energy(self) -> EnergyYield:
        """Return energy yield information for the whole system."""
        data = self.endpoint_data_results["LiveData"]
        power_now = int(data["Power"]["Total"]["PowerNow"])
        power_day = int(data["Power"]["Total"]["PowerTDY"])
        power_mtd = int(data["Power"]["Total"]["PowerMTD"])
        return EnergyYield(power_now, power_day, power_mtd)

    def consumption(self) -> EnergyYield:
        """Return load information for the whole system."""
        load = EnergyYield(0, 0, 0)
        for mtu in self.mtus:
            if mtu.type == MtuType.LOAD:
                load += mtu.energy()
        return load

    def production(self) -> EnergyYield:
        """Return generation information for the whole system."""
        gen = EnergyYield(0, 0, 0)
        for mtu in self.mtus:
            if mtu.type == MtuType.GENERATION:
                gen += mtu.energy()
        return gen

    def _mtu_energy(self, mtu: TedMtu) -> EnergyYield:
        """Return consumption or production information for a MTU."""
        data = self.endpoint_data_results["LiveData"]
        power_now = int(data["Power"]["MTU%d" % mtu.position]["PowerNow"])
        power_tdy = int(data["Power"]["MTU%d" % mtu.position]["PowerTDY"])
        power_mtd = int(data["Power"]["MTU%d" % mtu.position]["PowerMTD"])
        if mtu.type == MtuType.GENERATION:
            return EnergyYield(-power_now, -power_tdy, -power_mtd)
        return EnergyYield(power_now, power_tdy, power_mtd)

    def _mtu_power(self, mtu: TedMtu) -> Power:
        """Return power information for a MTU."""
        data = self.endpoint_data_results["LiveData"]
        power_now = int(data["Power"]["MTU%d" % mtu.position]["PowerNow"])
        ap_power = int(data["Power"]["MTU%d" % mtu.position]["KVA"])
        power_factor = 0.0
        if ap_power != 0:
            power_factor = round(((power_now / ap_power) * 100), 1)
        voltage = int(data["Voltage"]["MTU%d" % mtu.position]["VoltageNow"]) / 10
        return Power(ap_power, power_factor, voltage)

    def _parse_mtu_type(self, mtu_type: int) -> MtuType:
        switcher = {
            0: MtuType.LOAD,
            1: MtuType.GENERATION,
            2: MtuType.NET,
            3: MtuType.STAND_ALONE,
        }
        return switcher.get(mtu_type, MtuType.STAND_ALONE)

    def _parse_mtus(self) -> None:
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []

        num_mtus = int(self.endpoint_settings_results["SystemSettings"]["NumberMTU"])
        mtu_settings = self.endpoint_settings_results["SystemSettings"]["MTUs"]["MTU"]
        solar_settings = self.endpoint_settings_results["SystemSettings"]["Solar"]
        for mtu_doc in mtu_settings[0:num_mtus]:
            mtu_number = int(mtu_doc["MTUNumber"])
            mtu = TedMtu(
                mtu_doc["MTUID"],
                mtu_number,
                mtu_doc["MTUDescription"],
                self._parse_mtu_type(int(solar_settings["SolarConfig%d" % mtu_number])),
                int(mtu_doc["PowerCalibrationFactor"]),
                int(mtu_doc["VoltageCalibrationFactor"]),
                self,
            )
            self.mtus.append(mtu)
