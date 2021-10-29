"""Base class for TED energy meters."""
from typing import Any, List, NamedTuple
from dataclasses import dataclass
import logging
import xmltodict
import httpx

from .formatting import (
    format_consumption,
    format_ct,
    format_ctgroup,
    format_mtu,
    format_spyder,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class TedMtu:
    id: str
    position: int
    description: str
    type: int
    power_cal_factor: float
    voltage_cal_factor: float


@dataclass
class TedCt:
    position: int
    description: str
    type: int
    multiplier: int


@dataclass
class TedCtGroup:
    position: int
    description: str
    member_cts: List[TedCt]


@dataclass
class TedSpyder:
    position: int
    secondary: int
    mtu_parent: str
    ctgroups: List[TedCtGroup]


class Consumption(NamedTuple):
    now: int
    daily: int
    mtd: int


class MtuConsumption(NamedTuple):
    current_usage: int
    apparent_power: int
    power_factor: float
    voltage: float


class TED:
    """Instance of TED"""

    def __init__(self, host: str, async_client: httpx.AsyncClient = None) -> None:
        """Init the TED."""
        self.host = host.lower()

        self.mtus: List[TedMtu] = []
        self.spyders: List[TedSpyder] = []
        self._async_client = async_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Return the httpx client."""
        return self._async_client or httpx.AsyncClient()

    async def update(self) -> None:
        """Fetch data from the endpoints."""
        raise NotImplementedError()

    async def check(self) -> bool:
        """Check if the required endpoint are accessible."""
        raise NotImplementedError()

    @property
    def gateway_id(self) -> str:
        """Return the id / serial number for the gateway."""
        return "ted"

    def total_consumption(self) -> Consumption:
        """Return consumption information for the whole system."""
        raise NotImplementedError()

    def mtu_consumption(self, mtu: TedMtu) -> MtuConsumption:
        """Return consumption information for a MTU."""
        raise NotImplementedError()

    def spyder_ctgroup_consumption(
        self, spyder: TedSpyder, ctgroup: TedCtGroup
    ) -> Consumption:
        """Return consumption information for a spyder ctgroup."""
        raise NotImplementedError()

    async def _check_endpooint(self, url: str) -> bool:
        formatted_url = url.format(self.host)
        response = await self._async_fetch_with_retry(formatted_url)
        return response.status_code < 300

    async def _update_endpoint(self, attr: str, url: str) -> None:
        formatted_url = url.format(self.host)
        response = await self._async_fetch_with_retry(formatted_url)
        try:
            setattr(self, attr, xmltodict.parse(response.text))
        except xmltodict.expat.ExpatError:
            raise

        _LOGGER.debug("Fetched from %s: %s: %s", formatted_url, response, response.text)

    async def _async_fetch_with_retry(self, url: str, **kwargs: Any) -> Any:
        """Retry 3 times to fetch the url if there is a transport error."""
        for attempt in range(3):
            try:
                async with self.async_client as client:
                    return await client.get(url, timeout=30, **kwargs)
            except httpx.TransportError:
                if attempt == 2:
                    raise

    def print_to_console(self) -> None:
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
