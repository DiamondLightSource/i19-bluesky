from typing import Literal

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator, make_decorator
from dodal.devices.i19.hutch_access import HutchAccessControl

from i19_bluesky.log import LOGGER


def check_access_control_before_run_wrapper(
    plan: MsgGenerator,
    access_device: HutchAccessControl,
    experiment_hutch: Literal["EH1", "EH2"],
):
    active_hutch = yield from bps.rd(access_device.active_hutch)

    def access_denied_plan() -> MsgGenerator:
        LOGGER.warning(f"Active hutch is {active_hutch}, plan will not run.")
        yield from bps.null()

    if active_hutch == experiment_hutch:
        yield from plan
    else:
        yield from access_denied_plan()


check_access_control = make_decorator(check_access_control_before_run_wrapper)
