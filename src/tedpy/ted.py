"""Base class for TED energy meters."""
import logging
from datetime import datetime
from typing import Any, List

import httpx
import xmltodict

from .dataclasses import EnergyYield, Power, SystemType, TedCtGroup, TedMtu, TedSpyder
from .formatting import (
    format_ct,
    format_ctgroup,
    format_energy_yield,
    format_mtu,
    format_spyder,
)

_LOGGER = logging.getLogger(__name__)


class TED:
    """Instance of TED."""

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

    @property
    def gateway_description(self) -> str:
        """Return the description for the gateway."""
        return ""

    def gateway_time(self) -> datetime:
        """Return the current time of the gateway."""
        raise NotImplementedError()

    @property
    def system_type(self) -> SystemType:
        """Return the system type of the gateway."""
        return SystemType.NET

    def energy(self) -> EnergyYield:
        """Return net energy yield information for the whole system."""
        raise NotImplementedError()

    def consumption(self) -> EnergyYield:
        """Return energy load of the whole system."""
        raise NotImplementedError()

    def production(self) -> EnergyYield:
        """Return energy generated by the whole system."""
        raise NotImplementedError()

    def _mtu_energy(self, mtu: TedMtu) -> EnergyYield:
        """Return consumption or production information for a MTU."""
        raise NotImplementedError()

    def _mtu_power(self, mtu: TedMtu) -> Power:
        """Return power information for a MTU."""
        raise NotImplementedError()

    def _ctgroup_energy(self, ctgroup: TedCtGroup) -> EnergyYield:
        """Return energy yield information for a spyder ctgroup."""
        raise NotImplementedError()

    async def _check_endpoint(self, url: str, params: str = None) -> bool:
        formatted_url = url.format(self.host, params)
        response = await self._async_fetch_with_retry(formatted_url)
        return response.status_code < 300

    async def _update_endpoint(self, attr: str, url: str, params: Any = None) -> None:
        formatted_url = url.format(self.host, params)
        response = await self._async_fetch_with_retry(formatted_url)
        try:
            if params is None:
                # write to self[attr]
                setattr(self, attr, xmltodict.parse(response.text))
            else:
                # write to self[attr][param]; assume self[attr] was initialized to dict()
                getattr(self, attr)[params] = xmltodict.parse(response.text)
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
        """Print all the settings and energy yield values to the console."""
        print("Gateway id:", self.gateway_id)
        print("Gateway description:", self.gateway_description)
        print("Gateway time:", self.gateway_time())
        print("Net Energy:", format_energy_yield(self.energy()))
        print("  Consumed:", format_energy_yield(self.consumption()))
        print("  Produced:", format_energy_yield(self.production()))
        print()

        print("MTUs:")
        for m in self.mtus:
            print("  " + format_mtu(m))
            print("    Energy:", format_energy_yield(m.energy()))
            print("    Power:", m.power())
        print()
        print("Spyders:")
        for s in self.spyders:
            print("  " + format_spyder(s))
            for g in s.ctgroups:
                print("    " + format_ctgroup(g))
                for c in g.member_cts:
                    print("      " + format_ct(c))
                print("      Energy:", format_energy_yield(g.energy()))
