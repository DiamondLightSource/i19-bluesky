# Create softIOC for mock access control

from softioc import asyncio_dispatcher, builder, softioc
from softioc.builder import records

if __name__ == "__main__":
    # Create an asyncio dispatcher, the event loop is now running
    dispatcher = asyncio_dispatcher.AsyncioDispatcher()

    # Set the record prefix
    builder.SetDeviceName("MOCK-ACCESS-CONTROL")

    # Create some records
    ao = builder.stringOut(
        "hatchStatus",
        initial_value="EH1",
        always_update=True,
    )

    asub = records.aSub(  # type: ignore
        "EHStatus",
        FTA="STRING",
        FTVA="STRING",
    )

    # Boilerplate get the IOC started
    builder.LoadDatabase()
    softioc.iocInit(dispatcher)
    softioc.dbpf("MOCK-ACCESS-CONTROL:EHStatus.VALA", ao.get())  # type: ignore

    # Finally leave the IOC running with an non-interactive shell.
    softioc.non_interactive_ioc()
