from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import (
    HDFPanda,
    PandaBitMux,
    SeqTable,
    SeqTrigger,
)
from pydantic.dataclasses import dataclass

from i19_bluesky.log import LOGGER

DEG_TO_ENC_COUNTS = -16667
TIME_TO_US_SCALE = 1e6  # Panda sequencer prescaler will be set to us


@dataclass(frozen=True)
class DeviceSettingsConstants:
    PANDA_SERIAL_FILENAME = "panda_serial_config"
    PANDA_STANDARD_FILENAME = "panda_standard_config"
    PANDA_DIR = Path("i19-bluesky/src/i19_bluesky/panda_config_files").absolute()


def arm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the PandA.")
    yield from bps.abs_set(panda.seq[2].enable, PandaBitMux.ONE, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ONE, wait=True)  # type:ignore


def disarm_panda(panda: HDFPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the PandA.")
    yield from bps.abs_set(panda.seq[2].enable, PandaBitMux.ZERO, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore


def generate_panda_seq_table(
    phi_start: float,
    phi_end: float,
    phi_steps: int,  # no. of images to take
    time_between_images: float,
) -> SeqTable:
    rows = SeqTable()  # type: ignore

    start_forwards_position = int(phi_start * DEG_TO_ENC_COUNTS)
    start_backwards_position = int(phi_end * DEG_TO_ENC_COUNTS)

    delay_between_pulses = int(time_between_images * TIME_TO_US_SCALE)

    # NOTE Need to swap the columns around as DEG_TO_ENC converter is negative

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=start_forwards_position,
        repeats=phi_steps,
        time1=delay_between_pulses,
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=start_backwards_position,
        repeats=phi_steps,
        time1=delay_between_pulses,
        outa1=True,
    )

    return rows
