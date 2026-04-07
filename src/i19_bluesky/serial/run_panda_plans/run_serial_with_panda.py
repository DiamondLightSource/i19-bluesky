import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    end_run,
    run_on_collection_abort,
    trigger_panda,
)
from i19_bluesky.serial.setup_beamline_plans.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def setup_then_trigger_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment.
    Has contingencies to abort if any stage produces errors, before moving the
    diffractometer to its starting position. Designed to be called with BlueAPI.

    Args:
        parameters (SerialExperimentEh2): SerialExperimentEh2:
            detector_distance_mm (float): Distance to move in Z axis
            two_theta_deg (float) Distance to move in Two-Theta axis
            rot_axis_start (float): Starting phi position, in degrees.
            rot_axis_end (float): Ending phi position, in degrees.
            images_per_well (int): Number of images to take.
            exposure_time_s (float): Time between images, in seconds.
            aperture_request (PinColRequest): PinColRequest object (StrEnum)
        devices (SerialCollectionEh2PandaComposite): SerialCollectionEh2PandaComposite \
            class containing:
            diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
            backlight : Backlight controller object
            pinhole_collimator : Pinhole Collimator control object
            panda (HDFPanda): The fastcs PandA ophyd device.
            eiger (EigerDetector): the eiger detector device.
    """

    yield from setup_beamline_before_collection(parameters, devices)
    yield from trigger_panda(parameters, devices)


def run_serial_with_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        setup_then_trigger_panda(parameters, devices),
        except_plan=lambda: (yield from run_on_collection_abort(devices)),
        final_plan=lambda: (yield from end_run(parameters, devices)),
        auto_raise=False,
    )
