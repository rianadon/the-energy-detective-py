from pathlib import Path

import pytest
import respx
from httpx import Response

from tedpy import createTED
from tedpy.dataclasses import MtuType, YieldType


def _fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load_fixture(version: str, name: str) -> str:
    with open(_fixtures_dir() / version / name, "r") as read_in:
        return read_in.read()


@pytest.mark.asyncio
@respx.mock
async def test_ted_5000() -> None:
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

    assert reader.energy().type == YieldType.SYSTEM_NET
    assert reader.energy().now == 9632
    assert reader.energy().daily == 38553
    assert reader.energy().mtd == 277266

    assert len(reader.mtus) == 4
    assert reader.mtus[0].id == "109CE0"
    assert reader.mtus[0].description == "Pan 1"
    assert reader.mtus[0].type == MtuType.NET
    assert reader.mtus[0].power_cal_factor == 100
    assert reader.mtus[0].voltage_cal_factor == 100
    assert reader.mtus[1].id == "109CAD"
    assert reader.mtus[1].description == "Pan 2"
    assert reader.mtus[1].type == MtuType.NET
    assert reader.mtus[1].power_cal_factor == 100
    assert reader.mtus[1].voltage_cal_factor == 100
    assert reader.mtus[2].id == "109D3A"
    assert reader.mtus[2].description == "AC DN"
    assert reader.mtus[2].type == MtuType.STAND_ALONE
    assert reader.mtus[2].power_cal_factor == 100
    assert reader.mtus[2].voltage_cal_factor == 100
    assert reader.mtus[3].id == "109E8B"
    assert reader.mtus[3].description == "AC UP"
    assert reader.mtus[3].type == MtuType.STAND_ALONE
    assert reader.mtus[3].power_cal_factor == 100
    assert reader.mtus[3].voltage_cal_factor == 100

    assert reader.mtus[0].energy().type == YieldType.MTU
    assert reader.mtus[0].energy().now == 5840
    assert reader.mtus[0].energy().daily == 28611
    assert reader.mtus[0].energy().mtd == 227562
    assert reader.mtus[0].power().apparent_power == 6062
    assert reader.mtus[0].power().power_factor == 96.3
    assert reader.mtus[0].power().voltage == 119.7
    assert reader.mtus[1].energy().type == YieldType.MTU
    assert reader.mtus[1].energy().now == 438
    assert reader.mtus[1].energy().daily == 1845
    assert reader.mtus[1].energy().mtd == 9688
    assert reader.mtus[1].power().apparent_power == 462
    assert reader.mtus[1].power().power_factor == 94.8
    assert reader.mtus[1].power().voltage == 119.6
    assert reader.mtus[2].energy().type == YieldType.MTU
    assert reader.mtus[2].energy().now == 3354
    assert reader.mtus[2].energy().daily == 8097
    assert reader.mtus[2].energy().mtd == 40016
    assert reader.mtus[2].power().apparent_power == 3680
    assert reader.mtus[2].power().power_factor == 91.1
    assert reader.mtus[2].power().voltage == 118.9
    assert reader.mtus[3].energy().type == YieldType.MTU
    assert reader.mtus[3].energy().now == 0
    assert reader.mtus[3].energy().daily == 0
    assert reader.mtus[3].energy().mtd == 0
    assert reader.mtus[3].power().apparent_power == 0
    assert reader.mtus[3].power().power_factor == 0
    assert reader.mtus[3].power().voltage == 0


@pytest.mark.asyncio
@respx.mock
async def test_ted_6000() -> None:
    """Verify TED 6000 API."""
    respx.get("/api/LiveData.xml").mock(return_value=Response(404, text=""))
    respx.get("/api/SystemSettings.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "systemSettings.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=0&M=0").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_total.xml"))
    )
    respx.get("/api/SystemOverview.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "systemOverview.xml"))
    )
    respx.get("/api/SpyderData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "spyderData.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=255&M=1").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_mtu1.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=255&M=2").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_mtu2.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=255&M=3").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_mtu3.xml"))
    )

    reader = await createTED("127.0.0.1")
    await reader.update()

    assert reader.energy().type == YieldType.SYSTEM_NET
    assert reader.energy().now == 3313
    assert reader.energy().daily == 35684
    assert reader.energy().mtd == 943962

    assert len(reader.mtus) == 3
    assert reader.mtus[0].id == "10028B"
    assert reader.mtus[0].description == "Panel1"
    assert reader.mtus[0].type == MtuType.NET
    assert reader.mtus[0].power_cal_factor == 100.0
    assert reader.mtus[0].voltage_cal_factor == 100.0
    assert reader.mtus[1].id == "17061A"
    assert reader.mtus[1].description == "Subpanel"
    assert reader.mtus[1].type == MtuType.STAND_ALONE
    assert reader.mtus[1].power_cal_factor == 104.0
    assert reader.mtus[1].voltage_cal_factor == 100.0
    assert reader.mtus[2].id == "00013A"
    assert reader.mtus[2].description == "Solar"
    assert reader.mtus[2].type == MtuType.GENERATION
    assert reader.mtus[2].power_cal_factor == 100.0
    assert reader.mtus[2].voltage_cal_factor == 100.0

    assert reader.mtus[0].energy().type == YieldType.MTU
    assert reader.mtus[0].energy().now == 1591
    assert reader.mtus[0].energy().daily == 22846
    assert reader.mtus[0].energy().mtd == 705341
    assert reader.mtus[0].power().apparent_power == 3344
    assert reader.mtus[0].power().power_factor == 97.3
    assert reader.mtus[0].power().voltage == 123
    assert reader.mtus[1].energy().type == YieldType.MTU
    assert reader.mtus[1].energy().now == 5840
    assert reader.mtus[1].energy().daily == 28611
    assert reader.mtus[1].energy().mtd == 227562
    assert reader.mtus[1].power().apparent_power == 52
    assert reader.mtus[1].power().power_factor == 80.7
    assert reader.mtus[1].power().voltage == 123
    assert reader.mtus[2].energy().type == YieldType.MTU
    assert reader.mtus[2].energy().now == -438
    assert reader.mtus[2].energy().daily == -1845
    assert reader.mtus[2].energy().mtd == -9688
    assert reader.mtus[2].power().apparent_power == 0
    assert reader.mtus[2].power().power_factor == 0
    assert reader.mtus[2].power().voltage == 0

    assert len(reader.spyders) == 1
    spy = reader.spyders[0]
    assert len(spy.ctgroups) == 6
    assert spy.ctgroups[0].position == 0
    assert spy.ctgroups[0].description == "Obj1"
    assert len(spy.ctgroups[0].member_cts) == 1
    assert spy.ctgroups[0].member_cts[0].position == 0
    assert spy.ctgroups[0].member_cts[0].description == "Obj1"
    assert spy.ctgroups[0].member_cts[0].type == 0
    assert spy.ctgroups[0].member_cts[0].multiplier == 100
    assert len(spy.ctgroups[1].member_cts) == 3
    assert spy.ctgroups[1].member_cts[0].position == 0
    assert spy.ctgroups[1].member_cts[0].description == "Obj1"
    assert spy.ctgroups[1].member_cts[0].type == 0
    assert spy.ctgroups[1].member_cts[0].multiplier == 100
    assert spy.ctgroups[1].member_cts[1].position == 1
    assert spy.ctgroups[1].member_cts[1].description == "Obj2"
    assert spy.ctgroups[1].member_cts[1].type == 1
    assert spy.ctgroups[1].member_cts[1].multiplier == 100
    assert spy.ctgroups[1].member_cts[2].position == 2
    assert spy.ctgroups[1].member_cts[2].description == "Obj3"
    assert spy.ctgroups[1].member_cts[2].type == 0
    assert spy.ctgroups[1].member_cts[2].multiplier == 200
    assert len(spy.ctgroups[2].member_cts) == 1
    assert spy.ctgroups[2].member_cts[0].position == 2
    assert spy.ctgroups[2].member_cts[0].description == "Obj3"
    assert spy.ctgroups[2].member_cts[0].type == 0
    assert spy.ctgroups[2].member_cts[0].multiplier == 200
    assert len(spy.ctgroups[3].member_cts) == 1
    assert spy.ctgroups[3].member_cts[0].position == 3
    assert spy.ctgroups[3].member_cts[0].description == "Obj4"
    assert spy.ctgroups[3].member_cts[0].type == 0
    assert spy.ctgroups[3].member_cts[0].multiplier == 200
    assert len(spy.ctgroups[4].member_cts) == 1
    assert spy.ctgroups[4].member_cts[0].position == 4
    assert spy.ctgroups[4].member_cts[0].description == "Obj5"
    assert spy.ctgroups[4].member_cts[0].type == 0
    assert spy.ctgroups[4].member_cts[0].multiplier == 100
    assert len(spy.ctgroups[5].member_cts) == 1
    assert spy.ctgroups[5].member_cts[0].position == 5
    assert spy.ctgroups[5].member_cts[0].description == "Obj6"
    assert spy.ctgroups[5].member_cts[0].type == 0
    assert spy.ctgroups[5].member_cts[0].multiplier == 100
    assert spy.ctgroups[0].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[0].energy().now == 0
    assert spy.ctgroups[0].energy().daily == 0
    assert spy.ctgroups[0].energy().mtd == 1156
    assert spy.ctgroups[1].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[1].energy().now == 568
    assert spy.ctgroups[1].energy().daily == 4672
    assert spy.ctgroups[1].energy().mtd == 96045
    assert spy.ctgroups[2].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[2].energy().now == 0
    assert spy.ctgroups[2].energy().daily == 0
    assert spy.ctgroups[2].energy().mtd == 24141
    assert spy.ctgroups[3].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[3].energy().now == 0
    assert spy.ctgroups[3].energy().daily == 0
    assert spy.ctgroups[3].energy().mtd == 10034
    assert spy.ctgroups[4].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[4].energy().now == 473
    assert spy.ctgroups[4].energy().daily == 7968
    assert spy.ctgroups[4].energy().mtd == 253156
    assert spy.ctgroups[5].energy().type == YieldType.SPYDER_GROUP
    assert spy.ctgroups[5].energy().now == 0
    assert spy.ctgroups[5].energy().daily == 0
    assert spy.ctgroups[5].energy().mtd == 0
