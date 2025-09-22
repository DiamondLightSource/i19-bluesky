import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.zebra.zebra import ArmDemand, ArmingDevice

from i19_bluesky.log import LOGGER


def arm_zebra(
    zebra: ArmingDevice = inject("zebra"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the ZEBRA.")
    yield from bps.abs_set(zebra, ArmDemand.ARM, wait=True)


def disarm_zebra(
    zebra: ArmingDevice = inject("zebra"),  # noqa: B008
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the ZEBRA.")
    yield from bps.abs_set(zebra, ArmDemand.DISARM, wait=True)
