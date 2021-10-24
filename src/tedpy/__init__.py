"""Module to read energy consumption from a TED energy meter."""
from .ted5000 import TED5000
from .ted6000 import TED6000

TED_CLASSES = [TED5000, TED6000]


async def createTED(host, async_client=None):
    """Create the appropriate TED client."""
    for cls in TED_CLASSES:
        ted = cls(host, async_client)
        if await ted.check():
            return ted
    raise ValueError("Host is not a supported TED device.")
