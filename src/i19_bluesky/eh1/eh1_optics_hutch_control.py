"""Entry point plans that use access controlled devices to operate the optics
from eh1."""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.shutter import AccessControlledShutter

from i19_bluesky.log import LOGGER


def open_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to open the shutter from eh1.")
    yield from bps.abs_set(shutter, ShutterDemand.OPEN, wait=True)


def close_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to close the shutter from eh1.")
    yield from bps.abs_set(shutter, ShutterDemand.CLOSE, wait=True)
