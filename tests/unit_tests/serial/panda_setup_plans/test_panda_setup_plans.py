from unittest.mock import patch

from bluesky.run_engine import RunEngine
from numpy.testing import assert_array_equal
from ophyd_async.fastcs.panda import HDFPanda, SeqTable, SeqTrigger

from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.panda_setup_plans.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)


async def test_wait_between_setting_table_and_arming(
    mock_panda: HDFPanda, RE: RunEngine, parameters: SerialExperiment
):
    with (
        patch(
            "i19_bluesky.serial.panda_setup_plans.panda_setup_plans.load_panda_from_yaml"
        ),
        patch(
            "i19_bluesky.serial.panda_setup_plans.panda_setup_plans.bps.wait"
        ) as patch_wait,
    ):
        RE(setup_panda_for_rotation(parameters, mock_panda))
        patch_wait.assert_called_once_with(group="panda-setup", timeout=60)


async def test_setup_panda_for_rotation(
    devices: DeviceInput, parameters: SerialExperiment, RE: RunEngine
):
    with patch(
        "i19_bluesky.serial.panda_setup_plans.panda_setup_plans.load_panda_from_yaml"
    ) as patch_load:
        parameters.rot_axis_start = 4
        parameters.rot_axis_end = 5
        parameters.images_per_well = 25
        parameters.exposure_time_s = 0.1
        RE(setup_panda_for_rotation(parameters, devices.panda), group="panda-setup")
        patch_load.assert_called_once()

    assert await devices.panda.inenc[1].setp.get_value() == 3500  # type: ignore

    expected_seq_table: SeqTable = SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        repeats=25000,
        position=4000,
        time1=100,
        outa1=True,
    ) + SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        repeats=25000,
        position=5000,
        time1=100,
        outa1=True,
    )

    test_table = await devices.panda.seq[1].table.get_value()
    assert_array_equal(test_table.trigger, expected_seq_table.trigger)
    assert_array_equal(test_table.repeats, expected_seq_table.repeats)
    assert_array_equal(test_table.position, expected_seq_table.position)
    assert_array_equal(test_table.time1, expected_seq_table.time1)
    assert_array_equal(test_table.outa1, expected_seq_table.outa1)


async def test_reset_panda(mock_panda: HDFPanda, RE: RunEngine):
    with patch(
        "i19_bluesky.serial.panda_setup_plans.panda_setup_plans.load_panda_from_yaml"
    ) as patch_load:
        RE(reset_panda(mock_panda, group="reset panda"))
        patch_load.assert_called_once()

    assert (
        await mock_panda.outenc[1].val.get_value()  # type: ignore
        == "INENC1.VAL"
    )
    assert (
        await mock_panda.outenc[2].val.get_value()  # type: ignore
        == "INENC2.VAL"
    )
