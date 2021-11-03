"""Formatting helper functions for classes."""

from .dataclasses import EnergyYield, TedCt, TedCtGroup, TedMtu, TedSpyder


def format_energy_yield(energy_yield: EnergyYield) -> str:
    return "Now: {} kW, Today: {} kWh, Month-to-date: {} kWh".format(
        energy_yield.now / 1000,
        energy_yield.daily / 1000,
        energy_yield.mtd / 1000,
    )


def format_mtu(m: TedMtu) -> str:
    return "mtu #{}: {} (id={}): type={}, power_cal_factor={}, voltage_cal_factor={}".format(
        m.position,
        m.description,
        m.id,
        m.type,
        m.power_cal_factor,
        m.voltage_cal_factor,
    )


def format_spyder(s: TedSpyder) -> str:
    return "spyder #{}: secondary={}, mtu_parent={}".format(
        s.position, s.secondary, s.mtu_parent
    )


def format_ctgroup(g: TedCtGroup) -> str:
    return "ctgroup #{}: {}".format(g.position, g.description)


def format_ct(c: TedCt) -> str:
    return "ct #{}: {}: type={}, multiplier={}".format(
        c.position, c.description, c.type, c.multiplier
    )
