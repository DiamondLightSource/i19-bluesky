import bluesky.plan_stubs as bps
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
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.panda_setup_plans import reset_panda, setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda
from i19_bluesky.serial.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def setup_diffractometer(
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_steps: int,
    exposure_time: float,
) -> MsgGenerator:
    """Setup phi start posistion and velocity on the diffractometer.

    Args:
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position.
        phi_steps (int): Number of images to take.
        exposure_time(float): Time between images, in seconds."""
    yield from bps.abs_set(diffractometer.phi, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(diffractometer.phi.velocity, velocity)


def trigger_panda(
    panda: HDFPanda,
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        panda (HDFPanda): The fastcs PandA ophyd device.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
    """
    yield from setup_diffractometer(
        diffractometer,
        phi_start,
        phi_steps,
        exposure_time,
    )
    yield from setup_panda_for_rotation(
        panda,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Arm panda and move phi")
    yield from arm_panda(panda)
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)


def move_diffractometer_back(
    diffractometer: FourCircleDiffractometer, phi_start: float
) -> MsgGenerator:
    LOGGER.info("Move diffractometer back to start position")
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)


def run_panda_test(
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_panda(
            panda,
            diffractometer,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
        ),
        except_plan=lambda: (yield from abort_panda(diffractometer, panda)),
        final_plan=lambda: (
            yield from move_diffractometer_back(diffractometer, phi_start)
        ),
        auto_raise=False,
    )


def setup_then_trigger_panda(
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
        panda, eh2_diffractometer, phi_start, phi_end, phi_steps, exposure_time
    )


def main_entry_plan(
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
