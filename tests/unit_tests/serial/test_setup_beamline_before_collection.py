from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.serial.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta", [(200, 0), (100, 30), (80, 90)]
)
@pytest.mark.parametrize(
    "eh2_aperture",
    [
        (PinColRequest.PCOL20),
        (PinColRequest.PCOL100),
    ],
)
@patch("i19_bluesky.serial.setup_beamline_pre_collection.move_detector_stage")
@patch(
    "i19_bluesky.serial.setup_beamline_pre_collection.move_pin_col_to_requested_in_position"
)
@patch("i19_bluesky.serial.setup_beamline_pre_collection.move_backlight_out")
async def test_setup_beamline_before_collection(
    mock_move_backlight_out: MagicMock,
    mock_move_pin_col_to_requested_in_position: MagicMock,
    mock_move_detector_stage: MagicMock,
    detector_z: float,
    detector_two_theta: float,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    eh2_aperture: PinColRequest,
):
    RE(
        setup_beamline_before_collection(
            detector_z,
            detector_two_theta,
            eh2_backlight,
            eh2_diffractometer,
            pincol,
            eh2_aperture,
        )
    )
    mock_move_backlight_out.assert_called_once_with(eh2_backlight)
    mock_move_pin_col_to_requested_in_position.assert_called_once_with(
        eh2_aperture, pincol
    )
    mock_move_detector_stage.assert_called_once_with(
        eh2_diffractometer.det_stage,
        detector_z,
        detector_two_theta,
    )
