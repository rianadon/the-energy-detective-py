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
        return int(self.endpoint_data_results["LiveData"]["System"]["NumberMTU"])

    def total_consumption(self):
        """Return consumption information for the whole system."""
        data = self.endpoint_data_results["LiveData"]
        power = int(data["Power"]["Total"]["PowerNow"])
        return Consumption(power, 0, 0)

    def mtu_consumption(self, mtu):
        """Return consumption information for a MTU."""
        data = self.endpoint_data_results["LiveData"]
        power = int(data["Power"]["MTU%d" % mtu.position]["PowerNow"])
        voltage = int(data["Voltage"]["MTU%d" % mtu.position]["VoltageNow"])
        return MtuConsumption(power, 0, 0, voltage)

    def _parse_mtus(self):
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []

        for mtu in range(1, self.num_mtus + 1):
            self.mtus.append(TedMtu("-", mtu, "mtu %d" % mtu, 0, 0, 0))
