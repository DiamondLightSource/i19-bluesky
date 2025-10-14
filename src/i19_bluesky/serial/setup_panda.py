import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda._block import PandaBitMux, PulseBlock, SeqBlock

from i19_bluesky.log import LOGGER


def arm_panda(seq: SeqBlock, pulse_block: PulseBlock) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the PandA.")
    yield from bps.abs_set(seq.enable, PandaBitMux.ONE, wait=True)
    # yield from bps.abs_set(pulse_block, x, wait=True)


def disarm_panda(seq: SeqBlock, pulse_block: PulseBlock) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the PandA.")
    yield from bps.abs_set(seq.enable, PandaBitMux.ZERO, wait=True)
    # yield from bps.abs_set(pulse_block, x, wait=True)
