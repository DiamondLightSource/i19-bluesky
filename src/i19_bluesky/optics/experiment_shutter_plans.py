import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.shutter import HutchConditionalShutter


def open_hutch_shutter(shutter: HutchConditionalShutter) -> MsgGenerator:
    yield from bps.abs_set(shutter, ShutterDemand.OPEN)


def close_hutch_shutter(shutter: HutchConditionalShutter) -> MsgGenerator:
    yield from bps.abs_set(shutter, ShutterDemand.CLOSE)
