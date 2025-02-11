import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.shutter import HutchConditionalShutter

from i19_bluesky.log import LOGGER


def open_hutch_shutter(shutter: HutchConditionalShutter) -> MsgGenerator:
    LOGGER.info("Opening experiment shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.OPEN)


def close_hutch_shutter(shutter: HutchConditionalShutter) -> MsgGenerator:
    LOGGER.info("Closing experiment shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.CLOSE)
