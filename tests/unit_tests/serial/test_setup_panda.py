from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import PandaBitMux
from ophyd_async.testing import set_mock_value

from i19_bluesky.serial.setup_panda import (
    arm_panda,
    disarm_panda,
)


async def test_panda_arm(panda, RE: RunEngine):
    set_mock_value(panda.seq[1].enable, PandaBitMux.ZERO)
    set_mock_value(panda.pulse[1].enable, PandaBitMux.ZERO)
    RE(arm_panda(panda))
    assert await panda.seq[1].enable.get_value() == PandaBitMux.ONE
    assert await panda.pulse[1].enable.get_value() == PandaBitMux.ONE


async def test_panda_disarm(panda, RE: RunEngine):
    set_mock_value(panda.seq[1].enable, PandaBitMux.ONE)
    set_mock_value(panda.pulse[1].enable, PandaBitMux.ONE)
    RE(disarm_panda(panda))
    assert await panda.seq[1].enable.get_value() == PandaBitMux.ZERO
    assert await panda.pulse[1].enable.get_value() == PandaBitMux.ZERO
