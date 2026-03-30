from unittest.mock import MagicMock, call, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.core import get_mock_put

from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    setup_diffractometer,
)
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    end_run,
    run_on_collection_abort,
    trigger_panda,
)


async def test_setup_diffractometer(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
    parameters: SerialExperiment,
):

    RE(setup_diffractometer(parameters, eh2_diffractometer))
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_called_once_with(-5.0)

    mock_phi_velocity = get_mock_put(eh2_diffractometer.phi.velocity)
    mock_phi_velocity.assert_called_once_with(100.0)


@pytest.mark.parametrize(
    "well_positions,phival", [({1: [1, 2, 3]}, 5), ({2: [1, 2, 3]}, 10)]
)
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.trigger")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.abs_set")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.move_stage_x_and_z")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.reset_panda")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.disarm_panda")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.arm_panda")
@patch(
    "i19_bluesky.serial.run_panda_plans.panda_serial_collection.setup_panda_for_rotation"
)
@patch(
    "i19_bluesky.serial.run_panda_plans.panda_serial_collection.setup_diffractometer"
)
async def test_trigger_panda(
    mock_setup_diffractometer: MagicMock,
    mock_setup_panda_for_rotation: MagicMock,
    mock_arm_panda: MagicMock,
    mock_disarm_panda: MagicMock,
    mock_reset_panda: MagicMock,
    mock_move_stage_x_and_z: MagicMock,
    mock_set_value_for_params: MagicMock,
    mock_arm_or_disarm: MagicMock,
    well_positions: dict[int, tuple],
    phival: int,
    parameters: SerialExperiment,
    devices: DeviceInput,
    RE: RunEngine,
):
    parameters.well_position = well_positions
    parameters.rot_axis_start = 5
    parameters.rot_axis_end = 10
    parent_mock = MagicMock()
    parent_mock.attach_mock(mock_set_value_for_params, "mock_set_value_for_params")
    parent_mock.attach_mock(mock_move_stage_x_and_z, "mock_move_stage_x_and_z")
    parent_mock.attach_mock(mock_setup_diffractometer, "mock_setup_diffractometer")
    parent_mock.attach_mock(
        mock_setup_panda_for_rotation, "mock_setup_panda_for_rotation"
    )
    parent_mock.attach_mock(mock_arm_panda, "mock_arm_panda")
    parent_mock.attach_mock(mock_disarm_panda, "mock_disarm_panda")
    parent_mock.attach_mock(mock_reset_panda, "mock_reset_panda")
    parent_mock.attach_mock(mock_arm_or_disarm, "mock_arm_or_disarm")
    RE(trigger_panda(parameters, devices))
    expected_calls = [
        call.mock_setup_diffractometer(parameters, devices.diffractometer),
        call.mock_setup_panda_for_rotation(parameters, devices.panda),
        call.mock_arm_panda(devices.panda),
        call.mock_arm_or_disarm(devices.eiger.drv.detector.arm),
        call.mock_move_stage_x_and_z(1, 3, devices.diffractometer),
        call.mock_set_value_for_params(devices.diffractometer.phi, phival, wait=True),
    ]

    parent_mock.assert_has_calls(expected_calls, any_order=True)


@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.reset_panda")
@patch(
    "i19_bluesky.serial.run_panda_plans.panda_serial_collection.move_diffractometer_back"
)
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.trigger")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.disarm_panda")
async def test_end_run(
    mock_disarm_panda: MagicMock,
    mock_disarm_eiger: MagicMock,
    mock_move_diffractometer_back: MagicMock,
    mock_reset_panda: MagicMock,
    parameters: SerialExperiment,
    devices: DeviceInput,
    RE: RunEngine,
):
    RE(end_run(parameters, devices))
    mock_disarm_eiger.assert_called_once_with(devices.eiger.drv.detector.disarm)
    mock_move_diffractometer_back.assert_called_once_with(devices.diffractometer, -5)
    mock_disarm_panda.assert_called_once_with(devices.panda)
    mock_reset_panda.assert_called_once_with(devices.panda)


@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.bps.trigger")
@patch("i19_bluesky.serial.run_panda_plans.panda_serial_collection.disarm_panda")
async def test_run_on_collection_abort(
    mock_disarm_panda: MagicMock,
    mock_disarm_eiger: MagicMock,
    RE: RunEngine,
    devices: DeviceInput,
):
    RE(run_on_collection_abort(devices))
    get_mock_put(devices.diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_eiger.assert_called_once_with(devices.eiger.drv.detector.disarm)
    mock_disarm_panda.assert_called_once_with(devices.panda)
