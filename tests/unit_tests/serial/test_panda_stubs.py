# import numpy as np
from bluesky.run_engine import RunEngine

# from ophyd_async.fastcs.panda import PandaBitMux, SeqTable, SeqTrigger
from i19_bluesky.serial.panda_stubs import (
    # arm_panda_for_rotation,
    # reset_panda,
    setup_panda_for_rotation,
)
from i19_bluesky.serial.setup_panda import panda


async def test_arm_panda_for_rotation(panda: panda, RE: RunEngine):
    bps_wait_done = False
    RE(setup_panda_for_rotation(panda, 5, 4, 3, 2, 1))
    assert await panda.inenc[1].val.get_value() == 5000

    # need to write test for yaml stuff

    # expected_seq_table: SeqTable = SeqTable.row(
    # trigger=SeqTrigger.POSA_GT,
    # repeats=2,
    # position=4000,
    # time1=1,
    # outa1=True,
    # ) + SeqTable.row(
    # trigger=SeqTrigger.POSA_LT,
    # repeats=2,
    # position=3000,
    # time1=1,
    # outa1=True,
    # )

    # table = seq_table_readback

    # use np.testing.assert_array_equal

    assert bps_wait_done
