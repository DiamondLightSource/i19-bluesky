import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.hutch_shutter import HutchShutter, ShutterDemand
from dodal.devices.i19.hutch_access import HutchAccessControl

from i19_bluesky.log import LOGGER
from i19_bluesky.optics.check_access_control import HutchName, check_access_control


def operate_shutter_plan(
    from_hutch: HutchName,
    shutter_demand: ShutterDemand,
    shutter: HutchShutter = inject("shutter"),  # noqa: B008
    access_control: HutchAccessControl = inject("access_control"),  # noqa: B008
) -> MsgGenerator:
    LOGGER.debug(f"Trying to operate the hutch shutter from {from_hutch.value}")

    @check_access_control(access_control, from_hutch)
    def move_hutch_shutter(
        shutter: HutchShutter, request: ShutterDemand
    ) -> MsgGenerator:
        LOGGER.info(f"Moving experiment shutter to {request}.")
        yield from bps.abs_set(shutter, request, wait=True)

    yield from move_hutch_shutter(shutter, shutter_demand)
