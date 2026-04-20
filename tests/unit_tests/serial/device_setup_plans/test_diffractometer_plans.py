from unittest.mock import MagicMock, call

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import get_mock_put

from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
    move_diffractometer_back,
    setup_diffractometer,
)


async def test_move_diffractometer_back(
    serial_stages: XYZPhiStage,
    RE: RunEngine,
):
    RE(move_diffractometer_back(serial_stages, 4.0))
    mock_phi = get_mock_put(serial_stages.phi.user_setpoint)
    mock_phi.assert_called_once_with(4.0)


async def test_setup_diffractometer(
    serial_stages: XYZPhiStage,
    parameters: SerialExperimentEh2,
    RE: RunEngine,
):
    parameters.rot_axis_start = 6.0
    RE(setup_diffractometer(parameters.panda_rotation_params, serial_stages))
    mock_phi = get_mock_put(serial_stages.phi.user_setpoint)
    mock_phi.assert_called_once_with(6.0)

    mock_phi_velocity = get_mock_put(serial_stages.phi.velocity)
    mock_phi_velocity.assert_called_once_with(1)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta", [(200, 0), (100, 30), (80, 90)]
)
async def test_move_detector_stage(
    detector_z: float,
    detector_two_theta: float,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(
        move_detector_stage(
            eh2_diffractometer.det_stage, detector_z, detector_two_theta
        )
    )
    assert (
        await eh2_diffractometer.det_stage.det_z.user_readback.get_value() == detector_z
    )
    assert (
        await eh2_diffractometer.det_stage.two_theta.user_readback.get_value()
        == detector_two_theta
    )


async def test_move_order_det_z_first(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    parent = MagicMock()
    mock_det_z = get_mock_put(eh2_diffractometer.det_stage.det_z.user_setpoint)
    mock_two_theta = get_mock_put(eh2_diffractometer.det_stage.two_theta.user_setpoint)
    parent.attach_mock(mock_det_z, "det_z")
    parent.attach_mock(mock_two_theta, "two_theta")
    RE(move_detector_stage(eh2_diffractometer.det_stage, 120, 45))
    parent.assert_has_calls([call.det_z(120), call.two_theta(45)])


async def test_move_order_two_theta_first(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(move_detector_stage(eh2_diffractometer.det_stage, 80, 90))
    parent = MagicMock()
    mock_det_z = get_mock_put(eh2_diffractometer.det_stage.det_z.user_setpoint)
    mock_two_theta = get_mock_put(eh2_diffractometer.det_stage.two_theta.user_setpoint)
    parent.attach_mock(mock_det_z, "det_z")
    parent.attach_mock(mock_two_theta, "two_theta")
    RE(move_detector_stage(eh2_diffractometer.det_stage, 80, 90))
    parent.assert_has_calls([call.two_theta(90), call.det_z(80)])
