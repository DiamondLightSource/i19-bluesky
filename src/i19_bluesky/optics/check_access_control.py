from typing import Literal

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator, make_decorator
from dodal.devices.i19.hutch_access import HutchAccessControl


def check_hutch_access(
    access_device: HutchAccessControl, experiment_hutch: Literal["EH1", "EH2"]
):
    active_hutch = yield from bps.rd(access_device.active_hutch)
    if active_hutch == experiment_hutch:
        return True
    else:
        return False


def check_access_control_before_run_wrapper(
    plan: MsgGenerator, access_device: HutchAccessControl
):
    # active_hutch = yield from bps.rd(access_device.active_hutch)

    def access_denied_plan():
        yield from bps.null()

    yield from bpp.contingency_wrapper(plan, else_plan=access_denied_plan)
    # MAYBE?
    # Or maybe plan_mutator is better?
    pass


check_access_control = make_decorator(check_access_control_before_run_wrapper)
