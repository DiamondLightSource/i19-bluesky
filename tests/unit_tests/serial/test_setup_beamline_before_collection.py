import pytest
from bluesky.run_engine import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.core import set_mock_value

from i19_bluesky.serial.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,eh2_aperture,in_positions",
    [
        (200, 0, PinColRequest.PCOL20, [12, 34.5, 7.1, 28]),
        (80, 90, PinColRequest.PCOL100, [23.4, 22.1, 12, 18.7]),
    ],
)
async def test_setup_beamline_before_collection(
    detector_z: float,
    detector_two_theta: float,
    eh2_aperture: PinColRequest,
    in_positions: list[float],
    RE: RunEngine,
    eh2_diffractometer: FourCircleDiffractometer,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
):

    size = int(eh2_aperture.value.strip("um"))
    set_mock_value(pincol.mapt.pin_x.in_positions[size], in_positions[0])
    set_mock_value(pincol.mapt.pin_y.in_positions[size], in_positions[1])
    set_mock_value(pincol.mapt.col_x.in_positions[size], in_positions[2])
    set_mock_value(pincol.mapt.col_y.in_positions[size], in_positions[3])
    RE(
        setup_beamline_before_collection(
            detector_z,
            detector_two_theta,
            eh2_aperture,
            eh2_backlight,
            eh2_diffractometer,
            pincol,
        )
    )
    assert (
        await eh2_diffractometer.det_stage.det_z.user_readback.get_value() == detector_z
    )
    assert (
        await eh2_diffractometer.det_stage.two_theta.user_readback.get_value()
        == detector_two_theta
    )

    assert await eh2_backlight.position.get_value() == InOutUpper.OUT

    assert await pincol._pinhole.x.user_readback.get_value() == in_positions[0]
    assert await pincol._pinhole.y.user_readback.get_value() == in_positions[1]
    assert await pincol._collimator.x.user_readback.get_value() == in_positions[2]
    assert await pincol._collimator.y.user_readback.get_value() == in_positions[3]
