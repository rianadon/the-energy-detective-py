def format_consumption(consumption):
    return "Now: {} kW, Today: {} kWh, Month-to-date: {} kWh".format(
        consumption.now / 1000, consumption.daily / 1000, consumption.mtd / 1000
    )


def format_mtu(m):
    return "mtu #{}: {} (id={}): type={}, power_cal_factor={}, voltage_cal_factor={}".format(
        m.position,
        m.description,
        m.id,
        m.type,
        m.power_cal_factor,
        m.voltage_cal_factor,
    )


def format_spyder(s):
    return "spyder #{}: secondary={}, mtu_parent={}".format(
        s.position, s.secondary, s.mtu_parent
    )


def format_ctgroup(g):
    return "ctgroup #{}: {}".format(g.position, g.description)


def format_ct(c):
    return "ct #{}: {}: type={}, multiplier={}".format(
        c.position, c.description, c.type, c.multiplier
    )
