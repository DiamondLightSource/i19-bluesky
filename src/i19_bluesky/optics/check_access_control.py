from enum import Enum
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.hutch_access import HutchAccessControl

from i19_bluesky.log import LOGGER

P = ParamSpec("P")
R = TypeVar("R")


class HutchName(str, Enum):
    EH1 = "EH1"
    EH2 = "EH2"


def check_access(
    wrapped_plan: Callable[P, MsgGenerator],
) -> Callable[Concatenate[HutchName, HutchAccessControl, P], MsgGenerator]:
    @wraps(wrapped_plan)
    def safe_plan(
        experiment_hutch: HutchName,
        access_device: HutchAccessControl,
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        active_hutch = yield from bps.rd(access_device.active_hutch)

        def access_denied_plan() -> MsgGenerator:
            LOGGER.warning(f"Active hutch is {active_hutch}, plan will not run.")
            yield from bps.null()

        if active_hutch == experiment_hutch.value:
            yield from wrapped_plan(*args, **kwargs)
        else:
            yield from access_denied_plan()

    return safe_plan
