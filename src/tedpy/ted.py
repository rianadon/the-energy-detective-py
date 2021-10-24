"""Base class for TED energy meters."""
import asyncio
import logging
import xmltodict
from collections import namedtuple
import httpx

from .formatting import *

_LOGGER = logging.getLogger(__name__)

TedMtu = namedtuple(
    "TedMtu",
    ["id", "position", "description", "type", "power_cal_factor", "voltage_cal_factor"],
)
TedSpyder = namedtuple("TedSpyder", ["position", "secondary", "mtu_parent", "ctgroups"])
TedCt = namedtuple("TedCt", ["position", "description", "type", "multiplier"])
TedCtGroup = namedtuple("TedCtGroup", ["position", "description", "member_cts"])

Consumption = namedtuple("Consumption", ["now", "daily", "mtd"])
MtuConsumption = namedtuple(
    "MtuConsumption", ["current_usage", "apparent_power", "power_factor", "voltage"]
)


class TED:
    """Instance of TED"""

    def __init__(self, host, async_client=None):
        """Init the TED."""
        self.host = host.lower()

        self.mtus = []
        self.spyders = []
        self._async_client = async_client

    @property
    def async_client(self):
        """Return the httpx client."""
        return self._async_client or httpx.AsyncClient()

    async def update(self):
        """Fetch data from the endpoints."""
        raise NotImplementedError()

    async def check(self):
        """Check if the required endpoint are accessible."""
        raise NotImplementedError()

    @property
    def gateway_id(self):
        """Return the id / serial number for the gateway."""
        return "ted"

    def total_consumption(self):
        """Return consumption information for the whole system."""
        raise NotImplementedError()

    def mtu_consumption(self, mtu):
        """Return consumption information for a MTU."""
        raise NotImplementedError()

    def spyder_ctgroup_consumption(self, spyder, ctgroup):
        """Return consumption information for a spyder ctgroup."""
        raise NotImplementedError()

    async def _check_endpooint(self, url):
        formatted_url = url.format(self.host)
        response = await self._async_fetch_with_retry(formatted_url)
        return response.status_code < 300

    async def _update_endpoint(self, attr, url):
        formatted_url = url.format(self.host)
        response = await self._async_fetch_with_retry(formatted_url)
        try:
            setattr(self, attr, xmltodict.parse(response.text))
        except xmltodict.expat.ExpatError:
            raise

        _LOGGER.debug("Fetched from %s: %s: %s", formatted_url, response, response.text)

    async def _async_fetch_with_retry(self, url, **kwargs):
        """Retry 3 times to fetch the url if there is a transport error."""
        for attempt in range(3):
            try:
                async with self.async_client as client:
                    return await client.get(url, timeout=30, **kwargs)
            except httpx.TransportError:
                if attempt == 2:
                    raise

    def print_to_console(self):
        """Print all the settings and consumption values to the console."""
        print("Gateway id:", self.gateway_id)
        print("Consumption:", format_consumption(self.total_consumption()))
        print()

        print("MTUs:")
        for m in self.mtus:
            print("  " + format_mtu(m))
            print("    Consumption:", self.mtu_consumption(m))
        print()
        print("Spyders:")
        for s in self.spyders:
            print("  " + format_spyder(s))
            for g in s.ctgroups:
                print("    " + format_ctgroup(g))
                for c in g.member_cts:
                    print("      " + format_ct(c))
                consumption = self.spyder_ctgroup_consumption(s, g)
                print("      Consumption:", format_consumption(consumption))
