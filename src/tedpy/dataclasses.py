"""Classes for representing parts of a TED device."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, NamedTuple

if TYPE_CHECKING:
    from . import TED


class MtuType(Enum):
    """TED Defined MTU configuration types."""

    NET = 0
    LOAD = 1
    GENERATION = 2
    STAND_ALONE = 3


class EnergyYield(NamedTuple):
    """Represents yields from the various system components."""

    now: int
    daily: int
    mtd: int

    def __add__(self, other: tuple) -> EnergyYield:
        """Add two EnergyYield objects by adding each energy total."""
        if not isinstance(other, EnergyYield):
            raise ValueError("only EnergyYields can be added to EnergyYields")
        return EnergyYield(
            self.now + other.now, self.daily + other.daily, self.mtd + other.mtd
        )

    def __sub__(self, other: tuple) -> EnergyYield:
        """Subtract two EnergyYield objects by subtracting each energy total."""
        if not isinstance(other, EnergyYield):
            raise ValueError("only EnergyYields can be subtracted from EnergyYields")
        return EnergyYield(
            self.now - other.now, self.daily - other.daily, self.mtd - other.mtd
        )


class Power(NamedTuple):
    """Power information for an MTU."""

    apparent_power: int
    power_factor: float
    voltage: float


class SystemType(Enum):
    """Defines the various TED6000 System Types."""

    NET = 0
    NET_GEN = 1
    GEN_LOAD = 2


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
