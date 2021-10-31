"""Classes for representing parts of a TED device."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, NamedTuple

if TYPE_CHECKING:
    from . import TED


class YieldType(Enum):
    """Represents the different types of system yields."""

    SYSTEM_NET = 0
    SYSTEM_LOAD = 1
    SYSTEM_GENERATION = 2
    MTU = 3
    SPYDER_GROUP = 4


class MtuType(Enum):
    """TED Defined MTU configuration types."""

    NET = 0
    LOAD = 1
    GENERATION = 2
    STAND_ALONE = 3


class EnergyYield(NamedTuple):
    """Represents yields from the various system components."""

    type: YieldType
    now: int
    daily: int
    mtd: int


class Power(NamedTuple):
    """Power information for an MTU."""

    apparent_power: int
    power_factor: float
    voltage: float


@dataclass
class TedMtu:
    """MTU panel for the energy meter."""

    id: str
    position: int
    description: str
    type: MtuType
    power_cal_factor: float
    voltage_cal_factor: float
    _ted: TED

    def energy(self) -> EnergyYield:
        """Return energy yield information for the MTU."""
        return self._ted._mtu_energy(self)

    def power(self) -> Power:
        """Return power information for the MTU."""
        return self._ted._mtu_power(self)


@dataclass
class TedCt:
    """Individual reading on a Spyder."""

    position: int
    description: str
    type: int
    multiplier: int


@dataclass
class TedCtGroup:
    """Group of readings on a Spyder."""

    position: int
    spyder_position: int
    description: str
    member_cts: List[TedCt]
    _ted: TED

    def energy(self) -> EnergyYield:
        """Return energy yield information for the ctgroup."""
        return self._ted._ctgroup_energy(self)


@dataclass
class TedSpyder:
    """Spyder unit for the energy meter."""

    position: int
    secondary: int
    mtu_parent: str
    ctgroups: List[TedCtGroup]
