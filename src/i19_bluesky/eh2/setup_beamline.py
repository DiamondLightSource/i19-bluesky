import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.common.enums import InOutUpper
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.beamstop import BeamStop
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.log import LOGGER


def setup_beamline_for_collection(
    aperture: PinColRequest,
    backlight: BacklightPosition = inject("backlight"),
    beamstop: BeamStop = inject("beamstop"),
    pinhole_and_collimator: PinholeCollimatorControl = inject("pinhole_and_collimator"),
    group: str = "setup-beamline",
    wait: bool = True,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection.

    Currently, moves the backlight to its 'out' position, the beamstop to the 'in'
    position and the pinhole and collimator to the requested aperture.
    Once implemented it will also move the attenuator.

    Args:
        aperture_request (PinColRequest):
            Requested position of aperture
        backlight (BacklightPosition):
            Backlight device
        beamstop (Beamstop):
            Beamstop device
        pinhole_and_collimator (PinholeCollimatorControl):
            Pinhole Collimator device
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
