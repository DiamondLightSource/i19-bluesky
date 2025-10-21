from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import PandaBitMux

from i19_bluesky.serial.setup_panda import (
    arm_panda,
    disarm_panda,
)


async def test_panda_arm(panda, RE: RunEngine):
    await panda.seq[1].enable.set(PandaBitMux.ZERO)
    await panda.pulse[1].enable.set(PandaBitMux.ZERO)
    RE(arm_panda(panda))
    assert await panda.seq[1].enable.get_value() == PandaBitMux.ONE
    assert await panda.pulse[1].enable.get_value() == PandaBitMux.ONE


async def test_panda_disarm(panda, RE: RunEngine):
    await panda.seq[1].enable.set(PandaBitMux.ONE)
    await panda.pulse[1].enable.set(PandaBitMux.ONE)
    RE(disarm_panda(panda))
    assert await panda.seq[1].enable.get_value() == PandaBitMux.ZERO
    assert await panda.pulse[1].enable.get_value() == PandaBitMux.ZERO
