from pathlib import Path

import pytest
import respx
from httpx import Response

from tedpy import createTED
from tedpy.ted5000 import TED5000
from tedpy.ted6000 import TED6000


def _fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load_fixture(version, name) -> dict:
    with open(_fixtures_dir() / version / name, "r") as read_in:
        return read_in.read()


@pytest.mark.asyncio
@respx.mock
async def test_ted_5000():
    """Verify TED 5000 API."""
    respx.get("/api/SystemSettings.xml").mock(
        return_value=Response(200, text=_load_fixture("ted5000", "systemSettings.xml"))
    )
    respx.get("/api/LiveData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted5000", "liveData.xml"))
    )

    reader = await createTED("127.0.0.1")
    await reader.update()

    assert reader.gateway_id == "2154E6"
    assert reader.gateway_description == "Demo System"

    assert reader.total_consumption().now == 9632
    assert reader.total_consumption().daily == 38553
    assert reader.total_consumption().mtd == 277266

    assert reader.num_mtus == 4
    assert len(reader.mtus) == 4
    assert reader.mtus[0].id == '109CE0'
    assert reader.mtus[0].description == 'Pan 1'
    assert reader.mtus[0].type == TED5000.SolarConfigs.LOAD
    assert reader.mtus[0].power_cal_factor == 100
    assert reader.mtus[0].voltage_cal_factor == 100
    assert reader.mtus[1].id == '109CAD'
    assert reader.mtus[1].description == 'Pan 2'
    assert reader.mtus[1].type == TED5000.SolarConfigs.LOAD
    assert reader.mtus[1].power_cal_factor == 100
    assert reader.mtus[1].voltage_cal_factor == 100
    assert reader.mtus[2].id == '109D3A'
    assert reader.mtus[2].description == 'AC DN'
    assert reader.mtus[2].type == TED5000.SolarConfigs.STAND_ALONE
    assert reader.mtus[2].power_cal_factor == 100
    assert reader.mtus[2].voltage_cal_factor == 100
    assert reader.mtus[3].id == '109E8B'
    assert reader.mtus[3].description == 'AC UP'
    assert reader.mtus[3].type == TED5000.SolarConfigs.STAND_ALONE
    assert reader.mtus[3].power_cal_factor == 100
    assert reader.mtus[3].voltage_cal_factor == 100

    assert reader.mtu_value(reader.mtus[0]).now == 5840
    assert reader.mtu_value(reader.mtus[0]).apparent_power == 6062
    assert reader.mtu_value(reader.mtus[0]).power_factor == 96.3
    assert reader.mtu_value(reader.mtus[0]).voltage == 119.7
    assert reader.mtu_value(reader.mtus[1]).now == 438
    assert reader.mtu_value(reader.mtus[1]).apparent_power == 462
    assert reader.mtu_value(reader.mtus[1]).power_factor == 94.8
    assert reader.mtu_value(reader.mtus[1]).voltage == 119.6
    assert reader.mtu_value(reader.mtus[2]).now == 3354
    assert reader.mtu_value(reader.mtus[2]).apparent_power == 3680
    assert reader.mtu_value(reader.mtus[2]).power_factor == 91.1
    assert reader.mtu_value(reader.mtus[2]).voltage == 118.9

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

    assert reader.num_mtus == 3
    assert len(reader.mtus) == 3
    assert reader.mtus[0].id == '10028B'
    assert reader.mtus[0].description == 'Panel1'
    assert reader.mtus[0].type == TED6000.MtuType.NET
    assert reader.mtus[0].power_cal_factor == 100.0
    assert reader.mtus[0].voltage_cal_factor == 100.0
    assert reader.mtus[1].id == '17061A'
    assert reader.mtus[1].description == 'Subpanel'
    assert reader.mtus[1].type == TED6000.MtuType.STAND_ALONE
    assert reader.mtus[1].power_cal_factor == 104.0
    assert reader.mtus[1].voltage_cal_factor == 100.0
    assert reader.mtus[2].id == '00013A'
    assert reader.mtus[2].description == 'Solar'
    assert reader.mtus[2].type == TED6000.MtuType.GENERATION
    assert reader.mtus[2].power_cal_factor == 100.0
    assert reader.mtus[2].voltage_cal_factor == 100.0
    
    assert reader.mtu_value(reader.mtus[0]).now == 3254
    assert reader.mtu_value(reader.mtus[0]).apparent_power == 3344
    assert reader.mtu_value(reader.mtus[0]).power_factor == 97.3
    assert reader.mtu_value(reader.mtus[0]).voltage == 123
    assert reader.mtu_value(reader.mtus[1]).now == 42
    assert reader.mtu_value(reader.mtus[1]).apparent_power == 52
    assert reader.mtu_value(reader.mtus[1]).power_factor == 80.7
    assert reader.mtu_value(reader.mtus[1]).voltage == 123
    assert reader.mtu_value(reader.mtus[2]).now == 0
    assert reader.mtu_value(reader.mtus[2]).apparent_power == 0
    assert reader.mtu_value(reader.mtus[2]).power_factor == 0
    assert reader.mtu_value(reader.mtus[2]).voltage == 0

    spy = reader.spyders[0]
    assert spy.ctgroups[0].description == 'Obj1'
    assert spy.ctgroups[1].description == 'Obj2'
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).now == 568
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).daily == 4672
    assert reader.spyder_ctgroup_consumption(spy, spy.ctgroups[1]).mtd == 96045
    