from unittest.mock import patch

from bluesky.run_engine import RunEngine
from numpy.testing import assert_array_equal
from ophyd_async.fastcs.panda import HDFPanda, SeqTable, SeqTrigger

from i19_bluesky.serial.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)


async def test_wait_between_setting_table_and_arming(
    mock_panda: HDFPanda, RE: RunEngine
):
    with patch("i19_bluesky.serial.panda_setup_plans.bps.wait") as patch_wait:
        RE(setup_panda_for_rotation(mock_panda, 4, 5, 10, 2, 1))
        patch_wait.assert_called_once_with(group="panda-setup", timeout=60)


async def test_setup_panda_for_rotation(mock_panda: HDFPanda, RE: RunEngine):
    RE(setup_panda_for_rotation(mock_panda, 4, 5, 10, 2, 1), group="panda-setup")
    assert await mock_panda.inenc[1].setp.get_value() == 5000  # type: ignore

    # need to write test for yaml stuff

    expected_seq_table: SeqTable = SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        repeats=2,
        position=5000,
        time1=1,
        outa1=True,
    ) + SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        repeats=2,
        position=10000,
        time1=1,
        outa1=True,
    )

    test_table = await mock_panda.seq[1].table.get_value()
    assert_array_equal(test_table.trigger, expected_seq_table.trigger)
    assert_array_equal(test_table.repeats, expected_seq_table.repeats)
    assert_array_equal(test_table.position, expected_seq_table.position)
    assert_array_equal(test_table.time1, expected_seq_table.time1)
    assert_array_equal(test_table.outa1, expected_seq_table.outa1)


async def test_reset_panda(mock_panda: HDFPanda, RE: RunEngine):
    RE(reset_panda(mock_panda, group="reset panda"))
    assert (
        await mock_panda.outenc[1].val.get_value()  # type: ignore
        == "INENC1.VAL"
    )
    assert (
        await mock_panda.outenc[2].val.get_value()  # type: ignore
        == "INENC2.VAL"
    )
