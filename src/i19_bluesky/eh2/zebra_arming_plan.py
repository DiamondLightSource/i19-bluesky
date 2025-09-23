import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.zebra.zebra import ArmDemand, Zebra

from i19_bluesky.log import LOGGER


def arm_zebra(zebra: Zebra) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the ZEBRA.")
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.ARM, wait=True)


def disarm_zebra(zebra: Zebra) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the ZEBRA.")
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.DISARM, wait=True)
