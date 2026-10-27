import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.core import set_mock_value
from ophyd_async.fastcs.panda import HDFPanda, PandaBitMux, SeqTrigger

from i19_bluesky.serial.panda_plans.panda_stubs import (
    DEG_TO_ENC_COUNTS,
    arm_panda,
    disarm_panda,
    generate_panda_seq_table,
)


async def test_panda_arm(mock_panda: HDFPanda, RE: RunEngine):
    set_mock_value(mock_panda.seq[2].enable, PandaBitMux.ZERO)
    set_mock_value(mock_panda.pulse[1].enable, PandaBitMux.ZERO)  # type: ignore
    RE(arm_panda(mock_panda))
    assert await mock_panda.seq[2].enable.get_value() == PandaBitMux.ONE
    assert await mock_panda.pulse[1].enable.get_value() == PandaBitMux.ONE  # type: ignore


async def test_panda_disarm(mock_panda: HDFPanda, RE: RunEngine):
    set_mock_value(mock_panda.seq[2].enable, PandaBitMux.ONE)
    set_mock_value(mock_panda.pulse[1].enable, PandaBitMux.ONE)  # type: ignore
    RE(disarm_panda(mock_panda))
    assert await mock_panda.seq[2].enable.get_value() == PandaBitMux.ZERO
    assert await mock_panda.pulse[1].enable.get_value() == PandaBitMux.ZERO  # type: ignore


async def test_seq_table_generated_correctly():
    inputs = (2.0, 4.5, 25, 0.1)
    table_from_func = generate_panda_seq_table(*inputs)

    expected_positions = [int(2.0 * DEG_TO_ENC_COUNTS), int(4.5 * DEG_TO_ENC_COUNTS)]

    assert table_from_func.trigger == [SeqTrigger.POSA_LT, SeqTrigger.POSA_GT]
    assert table_from_func.repeats == pytest.approx([25, 25])
    assert table_from_func.position == pytest.approx(expected_positions)
    assert table_from_func.time1 == pytest.approx([100000, 100000])
    assert table_from_func.outa1 == pytest.approx([True, True])
