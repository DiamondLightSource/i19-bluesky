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

# DEG_TO_ENC_COUNTS = 1000
DEG_TO_ENC_COUNTS = -16667
TIME_TO_US_SCALE = 1e6  # Panda sequencer prescaler will be set to us
# DEG_TO_ENC_COUNTS = 1e-5
DEFAULT_PULSE_WIDTH_US = 50  # Eiger only sees rising edge anyway afaik


@dataclass(frozen=True)
class DeviceSettingsConstants:
    PANDA_SERIAL_CONFIG = "panda_serial_config"
    PANDA_STANDARD_CONFIG = "panda_standard_config"
    # NOTE needed full path on cluster
    PANDA_DIR = Path(
        "/dls_sw/i19-2/software/bluesky/i19-bluesky/src/i19_bluesky/panda_config_files"
    ).absolute()


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
    time_between_images: float,
) -> SeqTable:
    rows = SeqTable()  # type: ignore

    start_forwards_position = int(phi_start * DEG_TO_ENC_COUNTS)
    start_backwards_position = int(phi_end * DEG_TO_ENC_COUNTS)

    delay_between_pulses = int(time_between_images * TIME_TO_US_SCALE)

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=start_forwards_position,
        repeats=phi_steps,
        time1=delay_between_pulses,
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=start_backwards_position,
        repeats=phi_steps,
        time1=delay_between_pulses,
        outa1=True,
    )

    # rows += SeqTable.row(
    #     trigger=SeqTrigger.POSA_GT,
    #     position=start_forwards_position,
    #     repeats=phi_steps,
    #     time1=DEFAULT_PULSE_WIDTH_US,
    #     outa1=True,
    #     time2=delay_between_pulses - DEFAULT_PULSE_WIDTH_US,
    #     outa2=False,
    # )

    # rows += SeqTable.row(
    #     trigger=SeqTrigger.POSA_LT,
    #     position=start_backwards_position,
    #     repeats=phi_steps,
    #     time1=DEFAULT_PULSE_WIDTH_US,
    #     outa1=True,
    #     time2=delay_between_pulses - DEFAULT_PULSE_WIDTH_US,
    #     outa2=False,
    # )

    return rows


def setup_outenc_vals(panda: HDFPanda, group="setup_outenc_vals"):
    yield from bps.abs_set(panda.outenc[1].val, "ZERO", group=group)  # type: ignore
    # Moved to INENC4 as that's there the new serial stages are connected
    yield from bps.abs_set(panda.outenc[4].val, "INENC4.VAL", group=group)  # type: ignore
