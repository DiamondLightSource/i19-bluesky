import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import PandaBitMux, SeqTrigger
from ophyd_async.testing import set_mock_value

from i19_bluesky.serial.setup_panda import (
    arm_panda,
    disarm_panda,
    generate_panda_seq_table,
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


async def test_tables_are_same():
    inputs = (5.6, 6.7, 10, 5)
    table_from_func = generate_panda_seq_table(*inputs)

    assert table_from_func.trigger == [SeqTrigger.POSA_GT, SeqTrigger.POSA_LT]
    assert table_from_func.repeats == pytest.approx([10, 10])
    assert table_from_func.position == pytest.approx([5600, 6700])
    assert table_from_func.time1 == pytest.approx([5, 5])
    assert table_from_func.outa1 == pytest.approx([True, True])
