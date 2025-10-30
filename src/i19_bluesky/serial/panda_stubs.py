import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import (
    HDFPanda,
    PandaBitMux,
    SeqTable,
    SeqTrigger,
)

from i19_bluesky.log import LOGGER

DEG_TO_ENC_COUNTS = 1000


def arm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ONE, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ONE, wait=True)  # type:ignore


def disarm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore


def generate_panda_seq_table(
    phi_start: float,
    phi_end: float,
    phi_steps: int,  # no. of images to take
    time_between_images: int,
) -> SeqTable:
    rows = SeqTable()  # type: ignore

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=int(phi_start * DEG_TO_ENC_COUNTS),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=int(phi_end * DEG_TO_ENC_COUNTS),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    return rows


def setup_outenc_vals(panda: HDFPanda, group="setup_outenc_vals"):
    yield from bps.abs_set(panda.outenc[1].val, "ZERO", group=group)  # type: ignore
    yield from bps.abs_set(panda.outenc[2].val, "INENC1.VAL", group=group)  # type: ignore
