import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.cryostream import OxfordCryoStream

from i19_bluesky.log import LOGGER


def run_temperature_ramp(
    target_temp: float,
    ramp_rate: float = 360,
    cryostream: OxfordCryoStream = inject("cryostream"),
) -> MsgGenerator:
    LOGGER.info(f"Start a temperature ramp to {target_temp}K, with rate {360}K/h")
    yield from bps.abs_set(cryostream.ramp_rate, ramp_rate, wait=True)
    yield from bps.abs_set(cryostream.ramp_temp, target_temp, wait=True)
    yield from bps.trigger(cryostream.ramp)
