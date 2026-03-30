import pytest
from bluesky.run_engine import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
)
from ophyd_async.core import set_mock_value

from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.setup_beamline_plans.setup_beamline_pre_collection import (
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
    parameters: SerialExperiment,
    devices: DeviceInput,
):

    size = int(eh2_aperture.value.strip("um"))
    parameters["detector_distance_mm"] = detector_z
    parameters["two_theta_deg"] = detector_two_theta
    parameters["aperture_request"] = eh2_aperture
    set_mock_value(devices.pincol.mapt.pin_x.in_positions[size], in_positions[0])
    set_mock_value(devices.pincol.mapt.pin_y.in_positions[size], in_positions[1])
    set_mock_value(devices.pincol.mapt.col_x.in_positions[size], in_positions[2])
    set_mock_value(devices.pincol.mapt.col_y.in_positions[size], in_positions[3])
    RE(setup_beamline_before_collection(parameters, devices))
    assert (
        await devices.diffractometer.det_stage.det_z.user_readback.get_value()
        == detector_z
    )
    assert (
        await devices.diffractometer.det_stage.two_theta.user_readback.get_value()
        == detector_two_theta
    )

    assert await devices.backlight.position.get_value() == InOutUpper.OUT

    assert await devices.pincol._pinhole.x.user_readback.get_value() == in_positions[0]
    assert await devices.pincol._pinhole.y.user_readback.get_value() == in_positions[1]
    assert (
        await devices.pincol._collimator.x.user_readback.get_value() == in_positions[2]
    )
    assert (
        await devices.pincol._collimator.y.user_readback.get_value() == in_positions[3]
    )
