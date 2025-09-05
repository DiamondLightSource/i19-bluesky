import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.pin_col_stages import PinColControl

from i19_bluesky.log import LOGGER


def move_pin_col_out_of_beam(
    pincol: PinColControl, group: str = "pincol_out", wait: bool = True
) -> MsgGenerator:
    pinx_out = yield from bps.rd(pincol.config.pin_x_out)
    colx_out = yield from bps.rd(pincol.config.col_x_out)

    # TODO check is move can be used, as long as it moves motors in the right order
    LOGGER.info(f"Moving colx to out position {colx_out}")
    yield from bps.mv(pincol.collimator.x, colx_out, group=group)
    LOGGER.info(f"Moving pinx to out position {pinx_out}")
    yield from bps.mv(pincol.pinhole.x, pinx_out, group=group)

    if wait:
        yield from bps.wait(group=group)
