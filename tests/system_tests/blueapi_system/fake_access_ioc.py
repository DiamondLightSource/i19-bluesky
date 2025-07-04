# Import the basic framework components.
# import asyncio

from softioc import asyncio_dispatcher, builder, softioc

if __name__ == "__main__":
    # Create an asyncio dispatcher, the event loop is now running
    dispatcher = asyncio_dispatcher.AsyncioDispatcher()

    # Set the record prefix
    builder.SetDeviceName("MOCK-ACCESS-CONTROL")

    # Create some records
    ai = builder.stringIn("EHStatus.VALB", initial_value="EH1")
    ao = builder.stringOut(
        "EHstatus.VALA",
        initial_value="EH1",
        always_update=True,
        on_update=lambda v: ai.set(v),
    )

    # Boilerplate get the IOC started
    builder.LoadDatabase()
    softioc.iocInit(dispatcher)

    # # Start processes required to be run after iocInit
    # async def update():
    #     while True:
    #         ai.set(ai.get() + 1)
    #         await asyncio.sleep(1)

    # dispatcher(update)

    # Finally leave the IOC running with an interactive shell.
    softioc.interactive_ioc(globals())
