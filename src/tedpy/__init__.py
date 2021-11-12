"""Module to read energy consumption from a TED energy meter."""
import httpx

from .dataclasses import (
    EnergyYield,
    MtuType,
    Power,
    SystemType,
    TedCt,
    TedCtGroup,
    TedMtu,
    TedSpyder,
)
from .ted import TED
from .ted5000 import TED5000
from .ted6000 import TED6000

TED_CLASSES = [TED5000, TED6000]


async def createTED(host: str, async_client: httpx.AsyncClient = None) -> TED:
    """Create the appropriate TED client."""
    for cls in TED_CLASSES:
        ted = cls(host, async_client)
        if await ted.check():
            return ted
    raise ValueError("Host is not a supported TED device.")
