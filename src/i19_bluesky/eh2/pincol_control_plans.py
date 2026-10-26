import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.log import LOGGER


def move_pin_col_out_of_beam(
    pinhole_and_collimator: PinholeCollimatorControl = inject("pinhole_and_collimator"),
) -> MsgGenerator:
    LOGGER.info("Moving Pinhole and Collimator stages out")
    yield from bps.abs_set(pinhole_and_collimator, PinColRequest.OUT, wait=True)


def move_pin_col_to_requested_in_position(
    aperture: PinColRequest,
    pinhole_and_collimator: PinholeCollimatorControl = inject("pinhole_and_collimator"),
) -> MsgGenerator:
    LOGGER.info(
        f"Moving Pinhole and Collimator stages in to aperture: {aperture.value}"
    )
    yield from bps.abs_set(pinhole_and_collimator, aperture, wait=True)
