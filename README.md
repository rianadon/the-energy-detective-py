# TEDpy

Unofficial library for reading from The Energy Detective power meters

This library supports the TED5000 and TED6000 devices.

It is based on [@realumhelp]'s [ted6000py](https://github.com/realumhelp/ted6000py), Home Assistant's ted5000 implementation, and [@gtdiehl] and [@jesserizzo]'s [envoy_reader](https://github.com/gtdiehl/envoy_reader/). Also huge thanks to [@realumhelp] for helping write and review much of the code!

[@realumhelp]: https://github.com/realumhelp
[@gtdiehl]: https://github.com/gtdiehl
[@jesserizzo]: https://github.com/jesserizzo

## Usage

```python
from tedpy import createTED

HOST = 'ted6000'

# Use asyncio to deal with the async methods
try:
    reader = await createTED(HOST)
    await reader.update()
    reader.print_to_console() # Print all information
    print(reader.energy()) # Total energy
    print(reader.consumption()) # Load energy only
    print(reader.production()) # Generated energy only

    print(reader.mtus[0].energy()) # Energy per MTU
    print(reader.mtus[0].power())
    print(reader.spyders[0].ctgroups[0].energy()) # Energy per ctgroup

except httpx.HTTPError:
    # Handle connection errors from createTED and update
```

## Testing

To print out your energy meter's values, run `poetry run python -m tedpy`.

The module's tests can be run using `poetry run pytest` (make sure you `poetry install` first!).

## Development

1. Install dependencies: `poetry install`
2. Install pre-commit hooks: `poetry run pre-commit install`
3. Develop!

## Notes

### System types

The energy meter may be configured as 1 of 3 possible `SystemType`s: `NET`, `NET_GEN`, and `LOAD_GEN` (referred to in documentation as `NET_LOAD`). `NET`, `GEN`, and `LOAD` are the possible MTU types defined as the following:

- `NET`: Consumption from the grid
- `GEN`: Solar power production
- `LOAD`: Consumption from the grid, in the case where you are directly feeding the grid with solar

If you have not connected solar power to the meter, your system type is most likely `NET`. Otherwise, you are likely using `NET_GEN` type (measuring both grid consumption and solar power production). If you do not use an internal breaker for solar power and instead feed it directly back into the grid, you will have `LOAD_GEN` type.

The TED6000 API returns NET (net power), GEN (power generated), and LOAD (power consumed by appliances). Below is a table summarizing how these are populated for each system type. `-(x)` indicates `x` is negated. Calculated fields are italicized.

| SystemType | NET                                   | GEN                             | LOAD                                      |
|-------------|---------------------------------------|---------------------------------|-------------------------------------------|
| `NET`       | total consumption                     | 0                               | 0                                         |
| `NET_GEN`   | grid consumption                      | -(solar power produced)         | *grid consumption + solar power produced* |
| `LOAD_GEN`  | *grid consumption - solar production* | -(solar power produced to grid) | grid consumption                          |

When using the `.energy()`, `.production()`, and `.consumption()` methods, the original values of the GEN column are inverted, and `.consumption()` is populated for the `NET` type:

| SystemType | `.energy()`                           | `.production()`              | `.consumption()`                          |
|-------------|---------------------------------------|------------------------------|-------------------------------------------|
| `NET`       | total consumption                     | 0                            | total consumption                         |
| `NET_GEN`   | grid consumption                      | solar power produced         | *grid consumption + solar power produced* |
| `LOAD_GEN`  | *grid consumption - solar production* | solar power produced to grid | grid consumption                          |

### Inverted GEN values

To keep consistency with the `.consumption()` method, MTUs configured as `GEN` will additionally return positive `EnergyYield` values (i.e. their negative values will be inverted to positive values). It is recommended you format MTU values as such:

```python
data = "Production" if (mtu.type == MtuType.GENERATION) else "Consumption"
return f"{mtu.description} {data}: {mtu.energy()}"
```

### TED5000 consumption and production

The TED5000 API does not return a total system `.production()` and `.consumption()` value, so the library calculates one itself.
Production is defined as the energy sum of all MTUs marked as type "LOAD", and Consumption is defined as the energy sum of all MTUs marked as type "GEN".

NET and stand-alone types of MTUs are not included in these totals, whereas they are included in the `.energy()` total of the system.

### TED5000 power factor

See [#7](https://github.com/rianadon/the-energy-detective-py/issues/7) for info on how the power factor is calculated. There is a field returned by the API, but the documentation does not mention this field so the power factor is instead calculated manually.
