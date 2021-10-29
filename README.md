# TEDpy

Unofficial library for reading from The Energy Detective power meters

This library supports the TED5000 and TED6000 devices.

It is based on @realumhelp's [ted6000py](https://github.com/realumhelp/ted6000py), Home Assistant's ted5000 implementation, and @gtdiehl and @jesserizzo's [envoy_reader](https://github.com/gtdiehl/envoy_reader/). Also huge thanks to @realumhelp for patching support for consumption/production distinction!

## Usage

```python
from tedpy import createTED

HOST = 'ted6000'

# Use asyncio to deal with the async methods
reader = await createTED(HOST)
await reader.update()
reader.print_to_console()
```

## Testing

To print out your energy meter's values, run `poetry run python -m tedpy`.

The module's tests can be run using `poetry run pytest` (make sure you `poetry install` first!).

## Development

1. Install dependencies: `poetry install`
2. Install pre-commit hooks: `poetry run pre-commit install`
3. Develop!
