from unittest.mock import MagicMock

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
async def test_setup_beamline_before_collection(
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
    assert (
        await eh2_diffractometer.det_stage.det_z.user_readback.get_value() == detector_z
    )
    assert (
        await eh2_diffractometer.det_stage.two_theta.user_readback.get_value()
        == detector_two_theta
    )
    mock_setup_beamline_before_collection = MagicMock()
    RE(
        mock_setup_beamline_before_collection(
            detector_z,
            detector_two_theta,
            eh2_backlight,
            eh2_diffractometer,
            pincol,
            eh2_aperture,
        )
    )
    mock_setup_beamline_before_collection.assert_called_once()
