from pathlib import Path

import pytest
import respx
from httpx import Response

from tedpy import createTED


def _fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load_fixture(version, name) -> dict:
    with open(_fixtures_dir() / version / name, "r") as read_in:
        return read_in.read()


@pytest.mark.asyncio
@respx.mock
async def test_ted_5000():
    """Verify TED 5000 API."""
    respx.get("/api/LiveData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted5000", "data.xml"))
    )

    reader = await createTED("127.0.0.1")
    await reader.update()

    assert reader.total_consumption().now == 3577
    assert len(reader.mtus) == 1
    assert reader.mtu_consumption(reader.mtus[0]).current_usage == 3577
    assert reader.mtu_consumption(reader.mtus[0]).voltage == 1198

@pytest.mark.asyncio
@respx.mock
async def test_ted_6000():
    """Verify TED 6000 API."""
    respx.get("/api/LiveData.xml").mock(return_value=Response(404, text=""))
    respx.get("/api/SystemSettings.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "systemSettings.xml"))
    )
    respx.get("/api/DashData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData.xml"))
    )
    respx.get("/api/SystemOverview.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "systemOverview.xml"))
    )
    respx.get("/api/SpyderData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "spyderData.xml"))
    )

    reader = await createTED("127.0.0.1")
    await reader.update()

    assert reader.total_consumption().now == 3313
    assert reader.total_consumption().daily == 35684
    assert reader.total_consumption().mtd == 943962

    assert reader.mtus[0].id == '1234'
    assert reader.mtus[0].description == 'Panel1'
    assert reader.mtu_consumption(reader.mtus[0]).current_usage == 3254
    assert reader.mtu_consumption(reader.mtus[0]).apparent_power == 3344
    assert reader.mtu_consumption(reader.mtus[0]).power_factor == 973
    assert reader.mtu_consumption(reader.mtus[0]).voltage == 123
    assert reader.mtu_consumption(reader.mtus[1]).voltage == 123

    spy = reader.spyders[0]
    assert spy.ctgroups[0].description == 'Obj1'
    assert spy.ctgroups[1].description == 'Obj2'
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).now == 568
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).daily == 4672
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).mtd == 96045
