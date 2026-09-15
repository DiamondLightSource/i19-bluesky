from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    trigger_panda_collection,
)


@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.complete")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.kickoff")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.abs_set")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.move_stage_x_and_z")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.arm_panda")
@patch(
    "i19_bluesky.serial.run_panda_plans.panda_serial_collection.setup_panda_for_rotation"
)
def test_trigger_panda_call_order(
    mock_setup_panda_for_rotation: MagicMock,
    mock_arm_panda: MagicMock,
    mock_move_stage_x_and_z: MagicMock,
    mock_set_value_for_params: MagicMock,
    mock_kickoff: MagicMock,
    mock_complete: MagicMock,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
):
    parameters.wells_to_collect = {"01": (0, 0, 0), "10": (1, 0, 0)}
    parameters.rot_axis_start = 5.0
    parent_mock = MagicMock()
    parent_mock.attach_mock(mock_set_value_for_params, "mock_set_value_for_params")
    parent_mock.attach_mock(mock_move_stage_x_and_z, "mock_move_stage_x_and_z")
    parent_mock.attach_mock(
        mock_setup_panda_for_rotation, "mock_setup_panda_for_rotation"
    )
    parent_mock.attach_mock(mock_arm_panda, "mock_arm_panda")
    parent_mock.attach_mock(mock_kickoff, "mock_kickoff")
    parent_mock.attach_mock(mock_complete, "mock_complete")
    RE(trigger_panda_collection(parameters, devices))
    expected_calls = [
        call.mock_setup_panda_for_rotation(
            parameters.panda_rotation_params, devices.panda
        ),
        call.mock_arm_panda(devices.panda),
        call.mock_kickoff(devices.eiger, wait=True),
        call.mock_move_stage_x_and_z(0, 0, devices.serial_stages),
        call.mock_move_stage_x_and_z(1, 0, devices.serial_stages),
        call.mock_set_value_for_params(devices.diffractometer.phi, 6.0, wait=True),
        call.mock_set_value_for_params(devices.diffractometer.phi, 5.0, wait=True),
        call.mock_complete(devices.eiger, wait=True),
    ]
    parent_mock.assert_has_calls(expected_calls, any_order=True)
