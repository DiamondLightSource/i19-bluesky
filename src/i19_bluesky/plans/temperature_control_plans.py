import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.cryostream import OxfordCryoStream

from i19_bluesky.log import LOGGER


def run_temperature_ramp(
    target_temp_in_k: float,
    ramp_rate: float = 360,
    cryostream: OxfordCryoStream = inject("cryostream"),
) -> MsgGenerator:
    """Trigger a temperature ramp on the cryostream.

    Args:
        target_temp_in_k (float): temperature to reach, in Kelvin.
        ramp_rate (float): temperature ramp rate, in K/h.
        cryostream: the cryostream device.
    """
    LOGGER.info(f"Start a temperature ramp to {target_temp_in_k}K, with rate {360}K/h")
    yield from bps.abs_set(cryostream.ramp_rate, ramp_rate, wait=True)
    yield from bps.abs_set(cryostream.ramp_temp, target_temp_in_k, wait=True)
    yield from bps.trigger(cryostream.ramp)
