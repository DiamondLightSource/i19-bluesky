import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.core import DetectorTrigger, TriggerInfo

from i19_bluesky.eh2.setup_beamline import setup_beamline_for_collection
from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.plans.optics_hutch_control_plans import open_experiment_shutter
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
    setup_sample_stage,
)
from i19_bluesky.serial.device_setup_plans.eiger_setup_plans import set_eiger_params


def setup_eh2_serial_collection(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Set up devices on the beamline for a serial collection.

    Performs the following tasks:
        * Reads energy and wavelength from dcm and sets up the detector
        * Moves the beamstop into the beam
        * Moves the backlight to its out position
        * Moves the pinhole and collimator to the requested aperture
        * TBD - move the attenuator to requested transmission
        * Sets up phi start and velocity on the sample stage
        * Moves the detector stage into place
        * Opens the experiment shutter

    """
    LOGGER.debug("Stage eiger")
    yield from bps.stage(devices.eiger, wait=True)
    # Read energy and wavelength from dcm to then set up eiger
    energ_in_kev = yield from bps.rd(devices.energy_device.energy_in_kev)
    wavelength_in_a = yield from bps.rd(devices.energy_device.wavelength_in_a)
    yield from set_eiger_params(
        parameters, energ_in_kev, wavelength_in_a, devices.eiger
    )
    # Set up beamline for collection
    yield from setup_beamline_for_collection(
        parameters.aperture_request,
        devices.backlight,
        devices.beamstop,
        devices.pinhole_and_collimator,
    )
    # Set up sample stage
    LOGGER.info("Set up sample stage phi axis")
    yield from setup_sample_stage(
        parameters.panda_rotation_params, devices.serial_stages
    )
    LOGGER.info("Moving detector stage into position")
    yield from move_detector_stage(
        devices.diffractometer.det_stage,
        parameters.detector_distance_mm,
        parameters.two_theta_deg,
    )

    # Set ntriggers
    # See https://github.com/bluesky/ophyd-async/issues/1288
    LOGGER.info(f"Set ntriggers to {parameters.total_num_images}")
    yield from bps.abs_set(
        devices.eiger.detector.ntrigger, parameters.total_num_images, wait=True
    )
    trigger_info = TriggerInfo(
        collections_per_event=1,
        number_of_events=1,
        trigger=DetectorTrigger.EXTERNAL_EDGE,
        livetime=parameters.exposure_time_s,
    )
    yield from bps.prepare(devices.eiger, trigger_info, wait=True)
    LOGGER.debug("Eiger prepare done!")

    # Open shutter
    yield from open_experiment_shutter(devices.shutter)
