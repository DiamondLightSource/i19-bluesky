from unittest.mock import MagicMock, call

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.core import get_mock_put

<<<<<<< HEAD
from i19_bluesky.eh2.move_detector_stage import move_detector_stage
=======
from i19_bluesky.eh2.move_detector_stage import move_stage
>>>>>>> f9418c7 (Added tests for moving detector stage)


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
<<<<<<< HEAD
        move_detector_stage(
            eh2_diffractometer.det_stage, detector_z, detector_two_theta
        )
=======
        move_stage(eh2_diffractometer.det_stage, detector_z, detector_two_theta)  # type: ignore
>>>>>>> f9418c7 (Added tests for moving detector stage)
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
<<<<<<< HEAD
    RE(move_detector_stage(eh2_diffractometer.det_stage, 120, 45))
=======
    RE(move_stage(eh2_diffractometer.det_stage, 120, 45))
>>>>>>> f9418c7 (Added tests for moving detector stage)
    parent.assert_has_calls([call.det_z(120), call.two_theta(45)])


async def test_move_order_two_theta_first(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
<<<<<<< HEAD
=======
    RE(move_stage(eh2_diffractometer.det_stage, 80, 90))
>>>>>>> f9418c7 (Added tests for moving detector stage)
    parent = MagicMock()
    mock_det_z = get_mock_put(eh2_diffractometer.det_stage.det_z.user_setpoint)
    mock_two_theta = get_mock_put(eh2_diffractometer.det_stage.two_theta.user_setpoint)
    parent.attach_mock(mock_det_z, "det_z")
    parent.attach_mock(mock_two_theta, "two_theta")
    RE(move_stage(eh2_diffractometer.det_stage, 80, 90))
<<<<<<< HEAD
    RE(move_detector_stage(eh2_diffractometer.det_stage, 80, 90))
=======
>>>>>>> f9418c7 (Added tests for moving detector stage)
    parent.assert_has_calls([call.two_theta(90), call.det_z(80)])
