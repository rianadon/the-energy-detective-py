import asyncio

from . import createTED


async def run() -> None:
    reader = await createTED(HOST)
    await reader.update()
    reader.print_to_console()


if __name__ == "__main__":
    HOST = input("Enter the TED meter address or host name: ")

    print("Reading...")
    loop = asyncio.get_event_loop()
    data_results = loop.run_until_complete(
        asyncio.gather(run(), return_exceptions=True)
    )

    print()
    print("Errors:", data_results)
