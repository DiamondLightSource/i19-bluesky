import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    end_run,
    run_on_collection_abort,
    trigger_panda,
)
from i19_bluesky.serial.setup_beamline_plans.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def setup_then_trigger_panda(
    well_positions: dict[
        int, tuple
    ],  # Currently a test, will be modified as we solidify parameters
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    eh2_backlight: BacklightPosition = inject("backlight"),
    pincol: PinholeCollimatorControl = inject("pincol"),
    panda: HDFPanda = inject("panda"),
    eiger: EigerDetector = inject("eiger"),
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment.
    Has contingencies to abort if any stage produces errors, before moving the
    diffractometer to its starting position. Designed to be called with BlueAPI.

    Args:
        detector_z (float): Distance to move in Z axis
        two_theta (float) Distance to move in Two-Theta axis
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
        aperture : PinColRequest object (StrEnum)
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        backlight : Backlight controller object
        pinhole_collimator : Pinhole Collimator control object
        panda (HDFPanda): The fastcs PandA ophyd device.
        eiger (EigerDetector): the eiger detector device.
    """
    yield from setup_beamline_before_collection(
        detector_z,
        detector_two_theta,
        eh2_aperture,
        eh2_backlight,
        eh2_diffractometer,
        pincol,
    )
    yield from trigger_panda(
        well_positions,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
        eh2_diffractometer,
        panda,
        eiger,
    )


def run_serial_with_panda(
    well_positions: dict[int, tuple],
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    eh2_backlight: BacklightPosition = inject("backlight"),
    pincol: PinholeCollimatorControl = inject("pincol"),
    panda: HDFPanda = inject("panda"),
    eiger: EigerDetector = inject("eiger"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        setup_then_trigger_panda(
            well_positions,
            detector_z,
            detector_two_theta,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            eh2_aperture,
            eh2_diffractometer,
            eh2_backlight,
            pincol,
            panda,
            eiger,
        ),
        except_plan=lambda: (
            yield from run_on_collection_abort(eh2_diffractometer, panda, eiger)
        ),
        final_plan=lambda: (
            yield from end_run(panda, eiger, eh2_diffractometer, phi_start)
        ),
        auto_raise=False,
    )
