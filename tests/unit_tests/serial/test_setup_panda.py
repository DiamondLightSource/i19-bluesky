from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import HDFPanda, PandaBitMux

from i19_bluesky.serial.setup_panda import (
    arm_panda,
    disarm_panda,
)


async def test_panda_arm(serial_panda: HDFPanda, RE: RunEngine):
    RE(arm_panda(serial_panda))
    assert await serial_panda.seq[1].enable.get_value() == PandaBitMux.ONE
    assert await serial_panda.pulse[1].enable.get_value() == PandaBitMux.ONE


async def test_panda_disarm(serial_panda: HDFPanda, RE: RunEngine):
    RE(disarm_panda(serial_panda))
    assert await serial_panda.seq[1].enable.get_value() == PandaBitMux.ZERO
    assert await serial_panda.pulse[1].enable.get_value() == PandaBitMux.ZERO
