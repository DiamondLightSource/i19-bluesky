import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.log import LOGGER


def move_pin_col_out_of_beam(
    pincol: PinholeCollimatorControl, group: str = "pincol_out", wait: bool = True
) -> MsgGenerator:
    LOGGER.info("Moving Pinhole and Collimator stages out")
    yield from bps.abs_set(pincol, "OUT")


def move_pin_col_to_requested_in_position(
    pincol: PinholeCollimatorControl,
    aperture: PinColRequest,
) -> MsgGenerator:
    LOGGER.info(
        f"Moving Pinhole and Collimator stages in to aperture: {aperture.value}"
    )
    yield from bps.abs_set(pincol, aperture)
