import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.zebra.zebra import SoftInState, Zebra

from i19_bluesky.log import LOGGER


def run_laser_plan(
    exposure_time_s: float, zebra: Zebra = inject("zebra")
) -> MsgGenerator:
    """When prompted from the UI, open the laser shutter on the sample for a set
    exposure time.

    Args:
        exposure_time_s (float): Time to keep the laser shutter open, in seconds.
        zebra (Zebra): The zebra device.
    """
    LOGGER.debug("Set OUT3_TTL on the zebra to SOFT_IN3")
    yield from bps.abs_set(
        zebra.output.out_ttl_pvs[3], zebra.mapping.sources.SOFT_IN3, wait=True
    )
    LOGGER.info(f"Open laser shutter for {exposure_time_s} s.")
    yield from bps.abs_set(zebra.inputs.soft_in_3, SoftInState.YES, wait=True)
    yield from bps.sleep(exposure_time_s)
    LOGGER.info("Close laser shutter")
    yield from bps.abs_set(zebra.inputs.soft_in_3, SoftInState.NO, wait=True)
