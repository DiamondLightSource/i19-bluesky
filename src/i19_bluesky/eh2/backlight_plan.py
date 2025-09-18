import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.common.enums import InOutUpper
from dodal.devices.i19.backlight import BacklightPosition

from i19_bluesky.log import LOGGER


def backlight_in(
    backlight: BacklightPosition = inject("backlight"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to move the backlight in.")
    yield from bps.abs_set(backlight, InOutUpper.IN, wait=True)


def backlight_out(
    backlight: BacklightPosition = inject("backlight"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to move the backlight out.")
    yield from bps.abs_set(backlight, InOutUpper.OUT, wait=True)
