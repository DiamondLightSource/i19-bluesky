from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.core import YamlSettingsProvider
from ophyd_async.fastcs.panda import (
    HDFPanda,
    PandaBitMux,
    SeqTable,
    SeqTrigger,
)
from ophyd_async.plan_stubs import apply_panda_settings, retrieve_settings
from pydantic.dataclasses import dataclass

from i19_bluesky.log import LOGGER

DEG_TO_ENC_COUNTS = 1000


@dataclass(frozen=True)
class DeviceSettingsConstants:
    PANDA_PC_FILENAME = "panda-pc"
    PANDA_THROUGH_ZEBRA = "panda-through-zebra"
    PANDA_DIR = Path("i19-bluesky/src/i19_bluesky/panda_config_files").absolute()


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

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=int(phi_start * DEG_TO_ENC_COUNTS),
        repeats=phi_steps * DEG_TO_ENC_COUNTS,
        time1=int(time_between_images * DEG_TO_ENC_COUNTS),
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=int(phi_end * DEG_TO_ENC_COUNTS),
        repeats=phi_steps * DEG_TO_ENC_COUNTS,
        time1=int(time_between_images * DEG_TO_ENC_COUNTS),
        outa1=True,
    )

    return rows


def setup_outenc_vals(panda: HDFPanda, group="setup_outenc_vals"):
    yield from bps.abs_set(panda.outenc[1].val, "ZERO", group=group)  # type: ignore
    yield from bps.abs_set(panda.outenc[2].val, "INENC1.VAL", group=group)  # type: ignore


def load_panda_from_yaml(yaml_directory: str, yaml_file_name: str, panda: HDFPanda):
    provider = YamlSettingsProvider(yaml_directory)
    settings = yield from retrieve_settings(provider, yaml_file_name, panda)
    yield from apply_panda_settings(settings)
