from collections.abc import Callable
from enum import Enum
from functools import wraps
from inspect import Parameter, signature
from typing import Concatenate, ParamSpec, TypeVar

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
    wrapped_plan: Callable[P, MsgGenerator[R]],
) -> Callable[Concatenate[HutchName, HutchAccessControl, P], MsgGenerator[R | None]]:
    @wraps(wrapped_plan)
    def safe_plan(
        experiment_hutch: HutchName,
        access_device: HutchAccessControl,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> MsgGenerator[R | None]:
        active_hutch = yield from bps.rd(access_device.active_hutch)

        if active_hutch == experiment_hutch.value:
            r = yield from wrapped_plan(*args, **kwargs)
            return r
        else:
            LOGGER.warning(f"Active hutch is {active_hutch}, plan will not run.")
            yield from bps.null()
            return None

    sig = signature(wrapped_plan)

    safe_plan.__signature__ = sig.replace(  # type: ignore
        parameters=[
            Parameter(
                name="experiment_hutch",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=HutchName,
            ),
            Parameter(
                name="access_device",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=HutchAccessControl,
            ),
            *list(sig.parameters.values()),
        ]
    )
    safe_plan.__annotations__.update(
        {"experiment_hutch": HutchName, "access_device": HutchAccessControl}
    )

    return safe_plan
