import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.beamstop import BeamStop
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.log import LOGGER


def setup_beamline_for_collection(
    aperture: PinColRequest,
    backlight: BacklightPosition,
    beamstop: BeamStop,
    pinhole_and_collimator: PinholeCollimatorControl,
    group: str = "setup-beamline",
    wait: bool = True,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection.

    Currently, moves the backlight to its 'out' position, the beamstop to the 'in'
    position and the pinhole and collimator to the requested aperture.
    Once implemented it will also move the attenuator.

    Args:
        aperture (PinColRequest): Requested position of aperture
        backlight (BacklightPosition): Backlight device
        beamstop (Beamstop): Beamstop device
        pinhole_and_collimator (PinholeCollimatorControl): Pinhole Collimator device
    """
    LOGGER.info("Beamline set up tasks")
    LOGGER.debug("Move beamstop in")
    yield from bps.abs_set(beamstop, InOutUpper.IN, group=group)
    LOGGER.debug("Move backlight out")
    yield from bps.abs_set(backlight, InOutUpper.OUT, group=group)
    LOGGER.debug(f"Pincol to {aperture}")
    yield from bps.abs_set(pinhole_and_collimator, aperture, group=group)
    LOGGER.debug("Set transmission not yet implemented")

    if wait:
        yield from bps.wait(group=group)


def setup_for_rotation(
    phi_position: float,
    omega_position: float,
    aperture: PinColRequest,
    backlight: BacklightPosition = inject("backlight"),
    beamstop: BeamStop = inject("beamstop"),
    pinhole_and_collimator: PinholeCollimatorControl = inject("pinhole_and_collimator"),
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator:
    """Set up the beamline for a standard rotation collection.

    Moves the phi and omega axes into the requested start position, waiting between the
    two moves as the collision control on the beamline won't allow the two motors to
    move concurrently. Also moves backlight, beamstop and pincol into position.

    Args:
        phi_position (float): Start position for the phi axis
        omega_position (float): Start position for the omega axis
        aperture (PinColRequest): Requested position of aperture
        backlight (BacklightPosition): Backlight device
        beamstop (Beamstop): Beamstop device
        pinhole_and_collimator (PinholeCollimatorControl): Pinhole Collimator device
        diffractometer (FourCircleDiffractometer): Newport device
    """
    LOGGER.info(f"Move omega to {omega_position}")
    yield from bps.abs_set(diffractometer.omega, omega_position, wait=True)
    LOGGER.info(f"Move phi to {phi_position}")
    yield from bps.abs_set(diffractometer.phi, phi_position)
    yield from setup_beamline_for_collection(
        aperture, backlight, beamstop, pinhole_and_collimator
    )
