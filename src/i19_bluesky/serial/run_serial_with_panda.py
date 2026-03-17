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
from dodal.devices.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.panda_serial_collection import (
    abort_panda,
    move_diffractometer_back,
    trigger_panda,
)
from i19_bluesky.serial.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def setup_then_trigger_panda(
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_eiger: EigerDetector = inject("eiger"),
    eh2_diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    eh2_backlight: BacklightPosition = inject("backlight"),
    pincol: PinholeCollimatorControl = inject("pincol"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment. \
    Has contingencies to abort if any stage produces errors, before moving the \
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
    """
    yield from setup_beamline_before_collection(
        detector_z,
        detector_two_theta,
        eh2_backlight,
        eh2_diffractometer,
        pincol,
        eh2_aperture,
    )
    yield from trigger_panda(
        panda,
        eh2_diffractometer,
        eh2_eiger,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
    )


def main_entry_plan(
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_eiger: EigerDetector = inject("eiger"),
    eh2_diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    eh2_backlight: BacklightPosition = inject("backlight"),
    pincol: PinholeCollimatorControl = inject("pincol"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        setup_then_trigger_panda(
            detector_z,
            detector_two_theta,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            eh2_aperture,
            eh2_eiger,
            eh2_diffractometer,
            eh2_backlight,
            pincol,
            panda,
        ),
        except_plan=lambda: (yield from abort_panda(eh2_diffractometer, panda)),
        final_plan=lambda: (
            yield from move_diffractometer_back(eh2_diffractometer, phi_start)
        ),
        auto_raise=False,
    )
