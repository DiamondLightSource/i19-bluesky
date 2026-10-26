from unittest.mock import patch

from bluesky.run_engine import RunEngine
from dodal.devices.motors import XYZPhiStage
from numpy.testing import assert_array_equal
from ophyd_async.fastcs.panda import HDFPanda, SeqTable, SeqTrigger

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.panda_plans.panda_setup_plans import (
    DEG_TO_ENC_COUNTS,
    reset_panda,
    setup_panda_for_rotation,
)


async def test_wait_between_setting_table_and_arming(
    mock_panda: HDFPanda,
    serial_stages: XYZPhiStage,
    RE: RunEngine,
    parameters: SerialExperimentEh2,
):
    with (
        patch("i19_bluesky.serial.panda_plans.panda_setup_plans.load_panda_from_yaml"),
        patch(
            "i19_bluesky.serial.panda_plans.panda_setup_plans.bps.wait"
        ) as patch_wait,
    ):
        RE(
            setup_panda_for_rotation(
                parameters.panda_rotation_params, mock_panda, serial_stages
            )
        )
        patch_wait.assert_called_once_with(group="panda-setup", timeout=60)


async def test_setup_panda_for_rotation(
    devices: SerialCollectionEh2PandaComposite,
    parameters: SerialExperimentEh2,
    RE: RunEngine,
):
    with patch(
        "i19_bluesky.serial.panda_plans.panda_setup_plans.load_panda_from_yaml"
    ) as patch_load:
        RE(
            setup_panda_for_rotation(
                parameters.panda_rotation_params, devices.panda, devices.serial_stages
            ),
            group="panda-setup",
        )
        patch_load.assert_called_once()

    assert (
        await devices.serial_stages.phi.user_readback.get_value()
        == parameters.panda_rotation_params.gate_start
    )
    assert (
        await devices.panda.inenc[4].setp.get_value()  # type: ignore
        == parameters.panda_rotation_params.gate_start * DEG_TO_ENC_COUNTS
    )
    assert await devices.panda.pulse[1].width.get_value() == parameters.exposure_time_s

    expected_seq_table: SeqTable = SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        repeats=10,
        position=0,  # Start at phi=0
        time1=100000,
        outa1=True,
    ) + SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        repeats=10,
        position=-16667,  # End at phi = 1
        time1=100000,
        outa1=True,
    )

    test_table = await devices.panda.seq[2].table.get_value()
    assert_array_equal(test_table.trigger, expected_seq_table.trigger)
    assert_array_equal(test_table.repeats, expected_seq_table.repeats)
    assert_array_equal(test_table.position, expected_seq_table.position)
    assert_array_equal(test_table.time1, expected_seq_table.time1)
    assert_array_equal(test_table.outa1, expected_seq_table.outa1)


async def test_reset_panda(mock_panda: HDFPanda, RE: RunEngine):
    with patch(
        "i19_bluesky.serial.panda_plans.panda_setup_plans.load_panda_from_yaml"
    ) as patch_load:
        RE(reset_panda(mock_panda))
        patch_load.assert_called_once()
