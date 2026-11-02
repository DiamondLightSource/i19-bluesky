import pytest
from bluesky import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.beamstop import BeamStop
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.core import set_mock_value

from i19_bluesky.eh2.setup_beamline import setup_beamline_for_collection


@pytest.mark.parametrize(
    "aperture, in_positions, expected_beamstop_x",
    [
        (PinColRequest.PCOL20, [12, 34.5, 7.1, 28], 5.0),
        (PinColRequest.PCOL100, [23.4, 22.1, 12, 18.7], 5.0),
    ],
)
async def test_setup_beamline_for_collection(
    aperture: PinColRequest,
    in_positions: list[float],
    expected_beamstop_x: float,
    pincol: PinholeCollimatorControl,
    eh2_backlight: BacklightPosition,
    beamstop: BeamStop,
    RE: RunEngine,
):

    size = int(aperture.value.strip("um"))
    set_mock_value(pincol.mapt.pin_x.in_positions[size], in_positions[0])
    set_mock_value(pincol.mapt.pin_y.in_positions[size], in_positions[1])
    set_mock_value(pincol.mapt.col_x.in_positions[size], in_positions[2])
    set_mock_value(
        pincol.mapt.col_y.in_positions[size],
        in_positions[3],
    )
    RE(
        setup_beamline_for_collection(
            aperture,
            eh2_backlight,
            beamstop,
            pincol,
        )
    )

    assert await eh2_backlight.position.get_value() == InOutUpper.OUT

    assert await beamstop.x.user_readback.get_value() == expected_beamstop_x

    assert await pincol._pinhole.x.user_readback.get_value() == in_positions[0]
    assert await pincol._pinhole.y.user_readback.get_value() == in_positions[1]
    assert await pincol._collimator.x.user_readback.get_value() == in_positions[2]
    assert await pincol._collimator.y.user_readback.get_value() == in_positions[3]
