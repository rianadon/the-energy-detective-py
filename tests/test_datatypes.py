from tedpy.dataclasses import EnergyYield


def test_energy_yield_addition() -> None:
    a = EnergyYield(1, 2, 3)
    b = EnergyYield(4, 5, 6)

    assert a + b == EnergyYield(5, 7, 9)


def test_energy_yield_subtraction() -> None:
    a = EnergyYield(1, 2, 3)
    b = EnergyYield(4, 5, 6)

    assert a - b == EnergyYield(-3, -3, -3)
