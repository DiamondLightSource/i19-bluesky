from collections.abc import Callable
from enum import Enum
from functools import wraps
from inspect import Parameter, signature
from typing import Concatenate, ParamSpec, TypeVar

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.hutch_access import HutchAccessControl

from i19_bluesky.exceptions import HutchInvalidError
from i19_bluesky.log import LOGGER

P = ParamSpec("P")
R = TypeVar("R")


HUTCH_INVALID_FLAG = "INVALID"


class HutchName(str, Enum):
    EH1 = "EH1"
    EH2 = "EH2"


def check_access(
    wrapped_plan: Callable[P, MsgGenerator[R]],
) -> Callable[Concatenate[HutchName, HutchAccessControl, P], MsgGenerator[R | None]]:
    """ Decorates the wrapped plan so that a check is done beforehand to verify \
    that the hutch making the request is the active hutch and that the plan can proceed.

    It the request dosn't come from the active hutch, the plan doesn't run and a \
    warning message is logged. This is useful for running tests without risking moving \
    hardware while the other hutch has beamtime.
    In case of the hutch state returning "INVALID", an error is raised.

    Args:
        wrapped_plan: the plan performing the run with its arguments plus:
            experiment_hutch (HutchName): The hutch requesting the plan to run
            access_device (HutchAccessControl): The device checking that the plan is \
                allowed to run

    Example:
    A plan like
        @check_access
        def my_plan(device) -> MsgGenerator:
            yield from bps.trigger(...)
            ...

    will be run client side with:
        blueapi controller run my_plan \
            '{"device":"device", "experiment_hutch":"EH2", \
                "access_device":"access_control"}'
    """

    @wraps(wrapped_plan)
    def safe_plan(
        experiment_hutch: HutchName,
        access_device: HutchAccessControl,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> MsgGenerator[R | None]:
        active_hutch = yield from bps.rd(access_device.active_hutch)

        if active_hutch == HUTCH_INVALID_FLAG:
            LOGGER.error("Active hutch value set to invalid, plan will not run.")
            raise HutchInvalidError(
                """Active hutch is INVALID, please contact beamline scientist
                to check for possible issue."""
            )

        if active_hutch == experiment_hutch.value:
            return (yield from wrapped_plan(*args, **kwargs))
        else:
            LOGGER.warning(f"Active hutch is {active_hutch}, plan will not run.")
            return (yield from bps.null())

    # NOTE For the pydantic model of the wrapped plan to be constructed correctly, it
    # is necessery to modify the signature and explicitely add the extra arguments from
    # the safe plan. This allows inspect to construct the correct Signature
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
