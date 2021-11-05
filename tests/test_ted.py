from pathlib import Path

import pytest
import respx
from httpx import Response

from tedpy import createTED
from tedpy.dataclasses import EnergyYield, MtuType, SystemType, TedCt


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

    assert reader.energy().now == 9632
    assert reader.energy().daily == 38553
    assert reader.energy().mtd == 277266

    assert reader.consumption() == EnergyYield(6278, 30456, 237250)
    assert reader.production() == EnergyYield(0, 0, 0)

    assert len(reader.mtus) == 4
    assert reader.mtus[0].id == "109CE0"
    assert reader.mtus[0].description == "Pan 1"
    assert reader.mtus[0].type == MtuType.LOAD
    assert reader.mtus[0].power_cal_factor == 100
    assert reader.mtus[0].voltage_cal_factor == 100
    assert reader.mtus[1].id == "109CAD"
    assert reader.mtus[1].description == "Pan 2"
    assert reader.mtus[1].type == MtuType.LOAD
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

    assert reader.mtus[0].energy() == EnergyYield(5840, 28611, 227562)
    assert reader.mtus[0].power().apparent_power == 6062
    assert reader.mtus[0].power().power_factor == 96.3
    assert reader.mtus[0].power().voltage == 119.7
    assert reader.mtus[1].energy() == EnergyYield(438, 1845, 9688)
    assert reader.mtus[1].power().apparent_power == 462
    assert reader.mtus[1].power().power_factor == 94.8
    assert reader.mtus[1].power().voltage == 119.6
    assert reader.mtus[2].energy() == EnergyYield(3354, 8097, 40016)
    assert reader.mtus[2].power().apparent_power == 3680
    assert reader.mtus[2].power().power_factor == 91.1
    assert reader.mtus[2].power().voltage == 118.9
    assert reader.mtus[3].energy() == EnergyYield(0, 0, 0)
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
    respx.get("/api/SystemOverview.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "systemOverview.xml"))
    )
    respx.get("/api/SpyderData.xml").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "spyderData.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=0&M=0").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_total.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=1&M=0").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_mtu1.xml"))
    )
    respx.get("/api/DashData.xml?T=0&D=2&M=0").mock(
        return_value=Response(200, text=_load_fixture("ted6000", "dashData_mtu3.xml"))
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

    assert reader.system_type == SystemType.NET_GEN

    assert reader.energy().now == 3313
    assert reader.energy().daily == 35684
    assert reader.energy().mtd == 943962

    assert reader.consumption().now == 1591
    assert reader.consumption().daily == 22846
    assert reader.consumption().mtd == 705341

    assert reader.production().now == 438
    assert reader.production().daily == 1845
    assert reader.production().mtd == 9688

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

    assert reader.mtus[0].energy() == EnergyYield(1591, 22846, 705341)
    assert reader.mtus[0].power().apparent_power == 3344
    assert reader.mtus[0].power().power_factor == 97.3
    assert reader.mtus[0].power().voltage == 123
    assert reader.mtus[1].energy() == EnergyYield(5840, 28611, 227562)
    assert reader.mtus[1].power().apparent_power == 52
    assert reader.mtus[1].power().power_factor == 80.7
    assert reader.mtus[1].power().voltage == 123
    assert reader.mtus[2].energy() == EnergyYield(438, 1845, 9688)
    assert reader.mtus[2].power().apparent_power == 0
    assert reader.mtus[2].power().power_factor == 0
    assert reader.mtus[2].power().voltage == 0

    assert len(reader.spyders) == 1
    spy = reader.spyders[0]
    assert len(spy.ctgroups) == 6
    [grp1, grp2, grp3, grp4, grp5, grp6] = spy.ctgroups

    assert grp1.position == 0
    assert grp1.description == "Obj1"

    assert grp1.member_cts == [TedCt(0, "Obj1", 0, 100)]
    assert grp2.member_cts == [
        TedCt(0, "Obj1", 0, 100),
        TedCt(1, "Obj2", 1, 100),
        TedCt(2, "Obj3", 0, 200),
    ]
    assert grp3.member_cts == [TedCt(2, "Obj3", 0, 200)]
    assert grp4.member_cts == [TedCt(3, "Obj4", 0, 200)]
    assert grp5.member_cts == [TedCt(4, "Obj5", 0, 100)]
    assert grp6.member_cts == [TedCt(5, "Obj6", 0, 100)]

    assert grp1.energy() == EnergyYield(0, 0, 1156)
    assert grp2.energy() == EnergyYield(568, 4672, 96045)
    assert grp3.energy() == EnergyYield(0, 0, 24141)
    assert grp4.energy() == EnergyYield(0, 0, 10034)
    assert grp5.energy() == EnergyYield(473, 7968, 253156)
    assert grp6.energy() == EnergyYield(0, 0, 0)
