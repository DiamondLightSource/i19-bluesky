from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import HDFPanda, SeqTable, SeqTrigger

from i19_bluesky.serial.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)

# async def test_wait_between_setting_table_and_arming


async def test_setup_panda_for_rotation(mock_panda: HDFPanda, RE: RunEngine):
    bps_wait_done = False
    RE(setup_panda_for_rotation(mock_panda, 5, 4, 3, 2, 1))
    assert await mock_panda.inenc[1].val.get_value() == 5000  # type: ignore

    # need to write test for yaml stuff

    expected_seq_table: SeqTable = SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        repeats=2,
        position=4000,
        time1=1,
        outa1=True,
    ) + SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        repeats=2,
        position=3000,
        time1=1,
        outa1=True,
    )

    assert mock_panda.seq[1].table == expected_seq_table

    assert bps_wait_done


async def test_reset_panda(mock_panda: HDFPanda, RE: RunEngine):
    RE(reset_panda(mock_panda, group="reset panda"))
    assert (
        await mock_panda.outenc[1].val.get_value()  # type: ignore
        == await mock_panda.inenc[1].val.get_value()  # type: ignore
    )
    assert (
        await mock_panda.outenc[2].val.get_value()  # type: ignore
        == await mock_panda.inenc[2].val.get_value()  # type: ignore
    )
