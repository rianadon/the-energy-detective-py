import asyncio
from typing import Any

import httpx

from .ted import TED, Consumption, MtuConsumption, TedMtu

ENDPOINT_URL_DATA = "http://{}/api/LiveData.xml"


class TED5000(TED):
    """Instance of TED5000."""

    def __init__(self, host: str, async_client: httpx.AsyncClient = None):
        """Init the TED5000."""
        super().__init__(host, async_client)

        self.endpoint_data_results: Any = None

    async def update(self) -> None:
        """Fetch data from the endpoints."""
        await asyncio.gather(
            self._update_endpoint("endpoint_data_results", ENDPOINT_URL_DATA),
        )

        self._parse_mtus()

    async def check(self) -> bool:
        """Check if the required endpoint are accessible."""
        return await self._check_endpooint(ENDPOINT_URL_DATA)

    @property
    def gateway_id(self) -> str:
        """Return the id / serial number for the gateway."""
        return "ted5000"

    def total_consumption(self) -> Consumption:
        """Return consumption information for the whole system."""
        data = self.endpoint_data_results["LiveData"]
        power = int(data["Power"]["Total"]["PowerNow"])
        return Consumption(power, 0, 0)

    def mtu_consumption(self, mtu: TedMtu) -> MtuConsumption:
        """Return consumption information for a MTU."""
        data = self.endpoint_data_results["LiveData"]
        power = int(data["Power"]["MTU%d" % mtu.position]["PowerNow"])
        voltage = int(data["Voltage"]["MTU%d" % mtu.position]["VoltageNow"])
        return MtuConsumption(power, 0, 0, voltage)

    def _parse_mtus(self) -> None:
        """Fill the list of MTUs with MTUs parsed from the xml data."""
        self.mtus = []

        num_mtus = int(self.endpoint_data_results["LiveData"]["System"]["NumberMTU"])
        for mtu in range(1, num_mtus + 1):
            self.mtus.append(TedMtu("-", mtu, "mtu %d" % mtu, 0, 0, 0))
