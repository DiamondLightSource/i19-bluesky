import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.hutch_shutter import HutchShutter, ShutterDemand

from i19_bluesky.log import LOGGER
from i19_bluesky.optics.check_access_control import check_access


@check_access
def operate_shutter_plan(
    shutter_demand: ShutterDemand,
    shutter: HutchShutter = inject("shutter"),
) -> MsgGenerator:
    LOGGER.info(f"Moving experiment shutter to {shutter_demand}.")
    yield from bps.abs_set(shutter, shutter_demand, wait=True)
