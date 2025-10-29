import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import HDFPanda, PandaBitMux, SeqTrigger
from ophyd_async.testing import set_mock_value

from i19_bluesky.serial.panda_stubs import (
    arm_panda,
    disarm_panda,
    generate_panda_seq_table,
    setup_outenc_vals,
)


async def test_panda_arm(mock_panda: HDFPanda, RE: RunEngine):
    set_mock_value(mock_panda.seq[1].enable, PandaBitMux.ZERO)
    set_mock_value(mock_panda.pulse[1].enable, PandaBitMux.ZERO)
    RE(arm_panda(mock_panda))
    assert await mock_panda.seq[1].enable.get_value() == PandaBitMux.ONE
    assert await mock_panda.pulse[1].enable.get_value() == PandaBitMux.ONE


async def test_panda_disarm(mock_panda: HDFPanda, RE: RunEngine):
    set_mock_value(mock_panda.seq[1].enable, PandaBitMux.ONE)
    set_mock_value(mock_panda.pulse[1].enable, PandaBitMux.ONE)
    RE(disarm_panda(mock_panda))
    assert await mock_panda.seq[1].enable.get_value() == PandaBitMux.ZERO
    assert await mock_panda.pulse[1].enable.get_value() == PandaBitMux.ZERO


async def test_tables_are_same():
    inputs = (5.6, 6.7, 10, 5)
    table_from_func = generate_panda_seq_table(*inputs)

    assert table_from_func.trigger == [SeqTrigger.POSA_GT, SeqTrigger.POSA_LT]
    assert table_from_func.repeats == pytest.approx([10, 10])
    assert table_from_func.position == pytest.approx([5600, 6700])
    assert table_from_func.time1 == pytest.approx([5, 5])
    assert table_from_func.outa1 == pytest.approx([True, True])


async def test_setup_outenc_vals(mock_panda: HDFPanda, RE: RunEngine):
    RE(setup_outenc_vals(mock_panda, group="setup_outenc_vals"))
    assert await mock_panda.outenc[1].val.get_value() == PandaBitMux.ZERO  # type: ignore
    assert (
        await mock_panda.outenc[2].val.get_value()  # type: ignore
        == "INENC1.VAL"()  # type: ignore
    )
