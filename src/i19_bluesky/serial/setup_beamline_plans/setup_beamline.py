import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.core import DetectorTrigger, TriggerInfo

from i19_bluesky.eh2.backlight_plan import move_backlight_out
from i19_bluesky.eh2.pincol_control_plans import move_pin_col_to_requested_in_position
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
    # Stage detector
    LOGGER.info("Stage detector")
    yield from bps.stage(devices.eiger)
    # Open shutter
    LOGGER.info("Open experiment shutter if EH2 is the active hutch")
    yield from open_experiment_shutter(devices.shutter)
    # Set up beamline for collection
    LOGGER.info("Set up the beamline before collection")
    yield from setup_beamline_for_collection(
        parameters.aperture_request,
        parameters.detector_distance_mm,
        parameters.two_theta_deg,
        devices.backlight,
        devices.pincol,
        devices.diffractometer,
    )
    # Set up sample stage
    LOGGER.info("Move phi to start")
    yield from setup_sample_stage(
        parameters.panda_rotation_params, devices.serial_stages
    )
    # Read energy and wavelength from dcm to then set up eiger
    LOGGER.info("Set up and prepare the eiger for collection")
    energ_in_kev = yield from bps.rd(devices.energy_device.energy_in_kev)
    wavelength_in_a = yield from bps.rd(devices.energy_device.wavelength_in_a)
    yield from set_eiger_params(
        parameters, energ_in_kev, wavelength_in_a, devices.eiger
    )
    # Set ntriggers
    # See https://github.com/bluesky/ophyd-async/issues/1288
    yield from bps.abs_set(
        devices.eiger.detector.ntrigger, parameters.total_num_images, wait=True
    )
    trigger_info = TriggerInfo(
        collections_per_event=1,
        number_of_events=1,
        trigger=DetectorTrigger.EXTERNAL_EDGE,
        livetime=parameters.exposure_time_s,
    )
    # Prepare
    yield from bps.prepare(devices.eiger, trigger_info, wait=True)


def setup_beamline_for_collection(
    aperture_request: PinColRequest,
    detector_distance_mm: float,
    two_theta_deg: float,
    backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection. Currently, moves the backlight to its
    'out' position, then moves the pinhole collimator to position to record at the
    requested aperture, a placeholder for moving the attenutator wedge, followed by
    a command to move the diffractometer an inputted distance in the X and Two-Theta
    axis.

    Args:
        aperture_request (PinColRequest):
            Requested position of aperture
        detector_distance_mm (float):
            Distance to move in the X axis
        two_theta_deg (float):
            Angle to move to in the theta axis
        backlight (BacklightPosition):
            Backlight device
        pincol (PinholeCollimatorControl):
            Pinhole Collimator device
        diffractometer (FourCircleDiffractometer):
            Diffractometer device
    """
    LOGGER.info("Moving backlight out")
    yield from move_backlight_out(backlight)
    LOGGER.info("Moving pinhole collimator into position")
    yield from move_pin_col_to_requested_in_position(aperture_request, pincol)
    LOGGER.info("Moving attenuator wedge")
    # waiting for https://github.com/DiamondLightSource/i19-bluesky/issues/8
    LOGGER.info("Moving detector stage into position")
    yield from move_detector_stage(
        diffractometer.det_stage,
        detector_distance_mm,
        two_theta_deg,
    )
