from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from ophyd_async.core import DetectorTrigger, TriggerInfo, set_mock_value

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import DEAD_TIME_S
from i19_bluesky.serial.run_panda_plans.setup_for_collection import (
    setup_eh2_serial_collection,
)


@patch("i19_bluesky.serial.run_panda_plans.setup_for_collection.set_eiger_params")
@patch(
    "i19_bluesky.serial.run_panda_plans.setup_for_collection.setup_beamline_for_collection"
)
@patch(
    "i19_bluesky.serial.run_panda_plans.setup_for_collection.open_experiment_shutter"
)
@patch("i19_bluesky.serial.run_panda_plans.setup_for_collection.bps.prepare")
async def test_setup_eh2_serial_collection(
    mock_prepare: MagicMock,
    mock_open_shutter: MagicMock,
    mock_setup: MagicMock,
    mock_set_eiger_params: MagicMock,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
):
    expected_trigger_info = TriggerInfo(
        collections_per_event=1,
        number_of_events=1,
        trigger=DetectorTrigger.EXTERNAL_EDGE,
        livetime=0.1,
    )
    expected_phi_velocity = parameters.rot_axis_increment / (
        parameters.exposure_time_s + DEAD_TIME_S
    )
    set_mock_value(devices.energy_device.energy_in_kev, 17.9)
    set_mock_value(devices.energy_device.wavelength_in_a, 0.6)
    RE(setup_eh2_serial_collection(parameters, devices))

    mock_open_shutter.assert_called_once_with(devices.shutter)
    mock_set_eiger_params.assert_called_once_with(parameters, 17.9, 0.6, devices.eiger)
    mock_setup.assert_called_once_with(
        "100um",
        devices.backlight,
        devices.beamstop,
        devices.pinhole_and_collimator,
    )

    assert await devices.serial_stages.phi.velocity.get_value() == expected_phi_velocity

    assert (
        await devices.serial_stages.phi.user_readback.get_value()
        == parameters.rot_axis_start
    )

    assert (
        await devices.diffractometer.det_stage.det_z.user_readback.get_value()
        == parameters.detector_distance_mm
    )
    assert (
        await devices.diffractometer.det_stage.two_theta.user_readback.get_value()
        == parameters.two_theta_deg
    )
    mock_prepare.assert_called_once_with(
        devices.eiger, expected_trigger_info, wait=True
    )
