"""Classes for representing parts of a TED device."""
from dataclasses import dataclass
from enum import Enum
from typing import List, NamedTuple


class MtuType(Enum):
    """TED Defined MTU configuration types."""

    NET = 0
    LOAD = 1
    GENERATION = 2
    STAND_ALONE = 3


@dataclass
class TedMtu:
    """MTU panel for the energy meter."""

    id: str
    position: int
    description: str
    type: MtuType
    power_cal_factor: float
    voltage_cal_factor: float


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
    description: str
    member_cts: List[TedCt]


@dataclass
class TedSpyder:
    """Spyder unit for the energy meter."""

    position: int
    secondary: int
    mtu_parent: str
    ctgroups: List[TedCtGroup]


class Consumption(NamedTuple):
    """Consumption for both totals and per Spyder."""

    now: int
    daily: int
    mtd: int


class MtuNet(NamedTuple):
    """Consumption or Production for an MTU."""

    type: MtuType
    now: int
    apparent_power: int
    power_factor: float
    voltage: float
