import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import HDFPanda, PandaBitMux

from i19_bluesky.log import LOGGER


def arm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ONE, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ONE, wait=True)  # type:ignore


def disarm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore
