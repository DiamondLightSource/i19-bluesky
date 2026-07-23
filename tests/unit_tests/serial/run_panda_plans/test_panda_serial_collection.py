from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine
from ophyd_async.core import get_mock_put

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    setup_sample_stage,
)
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    trigger_panda_collection,
)


async def test_setup_sample_stage(
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
    parameters: SerialExperimentEh2,
):

    RE(setup_sample_stage(parameters.panda_rotation_params, devices.serial_stages))
    mock_phi = get_mock_put(devices.serial_stages.phi.user_setpoint)
    mock_phi.assert_called_once_with(0.0)

    mock_phi_velocity = get_mock_put(devices.serial_stages.phi.velocity)
    mock_phi_velocity.assert_called_once_with(1.0)


@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.trigger")
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
    mock_arm_or_disarm: MagicMock,
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
    parent_mock.attach_mock(mock_arm_or_disarm, "mock_arm_or_disarm")
    RE(trigger_panda_collection(parameters, devices))
    expected_calls = [
        call.mock_setup_panda_for_rotation(
            parameters.panda_rotation_params, devices.panda
        ),
        call.mock_arm_panda(devices.panda),
        call.mock_arm_or_disarm(devices.eiger.detector.arm),
        call.mock_move_stage_x_and_z(0, 0, devices.serial_stages),
        call.mock_move_stage_x_and_z(1, 0, devices.serial_stages),
        call.mock_set_value_for_params(devices.diffractometer.phi, 6.0, wait=True),
        call.mock_set_value_for_params(devices.diffractometer.phi, 5.0, wait=True),
    ]
    parent_mock.assert_has_calls(expected_calls, any_order=True)
