from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
)
from ophyd_async.core import set_mock_value

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.setup_beamline_plans.setup_beamline import (
    read_energy_and_wavelength,
    setup_beamline_for_collection,
    setup_eh2_serial_collection,
)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,eh2_aperture,in_positions",
    [
        (200, 0, PinColRequest.PCOL20, [12, 34.5, 7.1, 28]),
        (80, 90, PinColRequest.PCOL100, [23.4, 22.1, 12, 18.7]),
    ],
)
async def test_setup_beamline_for_collection(
    detector_z: float,
    detector_two_theta: float,
    eh2_aperture: PinColRequest,
    in_positions: list[float],
    RE: RunEngine,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
):

    size = int(eh2_aperture.value.strip("um"))
    parameters.detector_distance_mm = detector_z
    parameters.two_theta_deg = detector_two_theta
    parameters.aperture_request = eh2_aperture
    set_mock_value(devices.pincol.mapt.pin_x.in_positions[size], in_positions[0])
    set_mock_value(devices.pincol.mapt.pin_y.in_positions[size], in_positions[1])
    set_mock_value(devices.pincol.mapt.col_x.in_positions[size], in_positions[2])
    set_mock_value(devices.pincol.mapt.col_y.in_positions[size], in_positions[3])
    RE(
        setup_beamline_for_collection(
            parameters.aperture_request,
            parameters.detector_distance_mm,
            parameters.two_theta_deg,
            devices.backlight,
            devices.pincol,
            devices.diffractometer,
        )
    )
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


async def test_read_energy_and_wavelength(
    devices: SerialCollectionEh2PandaComposite, RE: RunEngine
):
    set_mock_value(devices.energy_device.energy_in_kev, 17.9)
    set_mock_value(devices.energy_device.wavelength_in_a, 0.6)
    en, wl = RE(read_energy_and_wavelength(devices.energy_device)).plan_result  # type: ignore

    assert await devices.energy_device.energy_in_kev.get_value() == en
    assert await devices.energy_device.wavelength_in_a.get_value() == wl


@patch(
    "i19_bluesky.serial.setup_beamline_plans.setup_beamline.read_energy_and_wavelength"
)
@patch("i19_bluesky.serial.setup_beamline_plans.setup_beamline.setup_sample_stage")
@patch(
    "i19_bluesky.serial.setup_beamline_plans.setup_beamline.setup_beamline_for_collection"
)
@patch("i19_bluesky.serial.setup_beamline_plans.setup_beamline.open_experiment_shutter")
def test_setup_eh2_serial_collection(
    mock_open_shutter: MagicMock,
    mock_setup: MagicMock,
    mock_stage: MagicMock,
    mock_read: MagicMock,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
):
    set_mock_value(devices.energy_device.energy_in_kev, 17.9)
    set_mock_value(devices.energy_device.wavelength_in_a, 0.6)
    RE(setup_eh2_serial_collection(parameters, devices))

    mock_open_shutter.assert_called_once_with(devices.shutter)
    # mock_read.assert_called_once_with(devices.energy_device)
    mock_setup.assert_called_once_with(
        "100um", 320, 0, devices.backlight, devices.pincol, devices.diffractometer
    )
    mock_stage.assert_called_once_with(
        parameters.panda_rotation_params, devices.serial_stages
    )
