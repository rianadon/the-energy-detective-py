import asyncio
from . import createTED

if __name__ == "__main__":
    HOST = input("Enter the TED meter address or host name: ")

    print("Reading...")
    loop = asyncio.get_event_loop()
    TESTREADER = loop.run_until_complete(createTED(HOST))

    data_results = loop.run_until_complete(
        asyncio.gather(TESTREADER.update(), return_exceptions=True)
    )
    print("Errors:", data_results)

    TESTREADER.print_to_console()
