import asyncio

from .ted import *

ENDPOINT_URL_SETTINGS = "http://{}/api/SystemSettings.xml"
ENDPOINT_URL_DATA = "http://{}/api/LiveData.xml"


class TED5000(TED):
    """Instance of TED5000"""

    def __init__(self, host, async_client=None):
        super().__init__(host, async_client)

        self.endpoint_settings_results = None
        self.endpoint_data_results = None

    async def update(self):
        """Fetch data from the endpoints."""
        await asyncio.gather(
            self._update_endpoint("endpoint_settings_results", ENDPOINT_URL_SETTINGS),
            self._update_endpoint("endpoint_data_results", ENDPOINT_URL_DATA),
        )

        self._parse_mtus()

    async def check(self):
        """Check if the required endpoint are accessible."""
        return await self._check_endpoint(ENDPOINT_URL_DATA)

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
    def num_mtus(self):
        """Return the number of MTUs."""
        return int(self.endpoint_settings_results["SystemSettings"]["NumberMTU"])

    def total_consumption(self):
        """Return consumption information for the whole system."""
        data = self.endpoint_data_results["LiveData"]
        power_now = int(data["Power"]["Total"]["PowerNow"])
        power_day = int(data["Power"]["Total"]["PowerTDY"])
        power_mtd = int(data["Power"]["Total"]["PowerMTD"])
        return Consumption(power_now, power_day, power_mtd)

    def mtu_consumption(self, mtu):
        """Return consumption information for a MTU."""
        data = self.endpoint_data_results["LiveData"]
        power_now = int(data["Power"]["MTU%d" % mtu.position]["PowerNow"])
        ap_power = int(data["Power"]["MTU%d" % mtu.position]["KVA"])
        power_factor = 0
        if(ap_power > 0):
            power_factor = round(((power_now / ap_power) * 100), 1)
        voltage = int(data["Voltage"]["MTU%d" % mtu.position]["VoltageNow"])
        return MtuConsumption(power_now, ap_power, power_factor, voltage)

    def _parse_mtus(self):
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []

        mtu_settings = self.endpoint_settings_results["SystemSettings"]["MTUs"]["MTU"]
        solar_settings = self.endpoint_settings_results["SystemSettings"]["Solar"]
        for mtu_doc in mtu_settings:
            if(len(self.mtus) < self.num_mtus):
                mtu_id = mtu_doc["MTUID"]
                mtu_number = int(mtu_doc["MTUNumber"])
                mtu = TedMtu(
                    mtu_id,
                    mtu_number,
                    mtu_doc["MTUDescription"],
                    int(solar_settings["SolarConfig%d" % mtu_number]),
                    int(mtu_doc["PowerCalibrationFactor"]),
                    int(mtu_doc["VoltageCalibrationFactor"]),
                )
                self.mtus.append(mtu)
