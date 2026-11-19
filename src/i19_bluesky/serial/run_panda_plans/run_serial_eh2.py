import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.access_controlled.shutter import (
    AccessControlledShutter,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import DetectorTrigger, TriggerInfo
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.eh2.setup_beamline import setup_beamline_for_collection
from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.plans.optics_hutch_control_plans import (
    close_experiment_shutter,
    open_experiment_shutter,
)
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
    move_sample_stage_back,
    setup_sample_stage,
)
from i19_bluesky.serial.device_setup_plans.eiger_setup_plans import (
    set_collection_directory_and_filename,
    set_eiger_params,
)
from i19_bluesky.serial.panda_plans.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)
from i19_bluesky.serial.run_panda_plans.trigger_serial_collection import (
    trigger_serial_collection,
)


# Common setup plans - detector independent
def beamline_setup_tasks(
    parameters: SerialExperimentEh2, devices: SerialCollectionEh2PandaComposite
):
    LOGGER.info("Setup hardware for collection")
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

    yield from setup_panda_for_rotation(
        parameters.panda_rotation_params, devices.panda, devices.serial_stages
    )

    # Open shutter
    yield from open_experiment_shutter(devices.shutter)


def on_abort_plan(serial_stages: XYZPhiStage, exception: Exception) -> MsgGenerator:
    LOGGER.warning("ABORT CURRENT COLLECTION")
    LOGGER.warning(exception)
    yield from bps.abs_set(serial_stages.phi.motor_stop, 1, wait=True)


def clean_up_at_end(
    rot_axis_start: float,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    shutter: AccessControlledShutter,
):
    LOGGER.info("Disarm panda and reset configuration from yaml")
    yield from reset_panda(panda)
    yield from move_sample_stage_back(serial_stages, rot_axis_start)
    LOGGER.info("Close experiment shutter")
    yield from close_experiment_shutter(shutter)


# Actual collection plan
def main_collection_plan(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    # Things that need to be done once at start and that's it:
    yield from beamline_setup_tasks(parameters, devices)
    # Read energy and wavelength from dcm to then set up eiger
    energ_in_kev = yield from bps.rd(devices.energy_device.energy_in_kev)
    wavelength_in_a = yield from bps.rd(devices.energy_device.wavelength_in_a)
    yield from set_eiger_params(
        parameters, energ_in_kev, wavelength_in_a, devices.eiger
    )

    @bpp.stage_decorator([devices.eiger])
    @bpp.run_decorator()
    def _collect(
        filename_prefix: str, num_triggers: int, wells_to_collect: dict[str, tuple]
    ):
        # Create directory and update path provider
        parameters.collection_directory.mkdir(exist_ok=True)
        yield from set_collection_directory_and_filename(
            parameters.visit, parameters.dataset, filename_prefix
        )
        # Set ntriggers
        # See https://github.com/bluesky/ophyd-async/issues/1288
        LOGGER.info(f"Set ntriggers to {parameters.total_num_images}")
        yield from bps.abs_set(devices.eiger.detector.ntrigger, num_triggers, wait=True)
        trigger_info = TriggerInfo(
            collections_per_event=1,
            number_of_events=1,
            trigger=DetectorTrigger.EXTERNAL_EDGE,
            livetime=parameters.exposure_time_s,
        )
        yield from bps.prepare(devices.eiger, trigger_info, wait=True)
        LOGGER.debug("Eiger prepare done!")

        yield from trigger_serial_collection(
            parameters.panda_rotation_params.scan_start_deg,
            parameters.panda_rotation_params.scan_end_deg,
            wells_to_collect,
            devices.eiger,
            devices.serial_stages,
        )

    num = 1
    filename_template = f"{parameters.filename_prefix}_%02d"
    for n, run in zip(parameters.num_images_per_run, parameters.run_list, strict=True):
        filename_prefix = filename_template % num
        # DO the collection
        yield from _collect(filename_prefix, n, run)
        # Update filenumber
        num += 1


# Entry point
@bpp.run_decorator()
def run_eiger_collection(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        main_collection_plan(parameters, devices),
        except_plan=lambda e: (yield from on_abort_plan(devices.serial_stages, e)),
        final_plan=lambda: (
            yield from clean_up_at_end(
                parameters.rot_axis_start,
                devices.panda,
                devices.serial_stages,
                devices.shutter,
            )
        ),
        auto_raise=False,
    )
