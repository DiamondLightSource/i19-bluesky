"""
i19 PandA setup plan for serial collection.
"""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.plans.load_panda_yaml import load_panda_from_yaml
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.panda_stubs import (
    DeviceSettingsConstants,
    arm_panda,
    generate_panda_seq_table,
    setup_outenc_vals,
)

DEG_TO_ENC_COUNTS = 1000
GENERAL_TIMEOUT = 60


def setup_panda_for_rotation(
    panda: HDFPanda,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
) -> MsgGenerator:
    """Configures the PandA device for phi forward and backward rotation"""

    yield from bps.stage(panda, group="panda-setup")

    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_PC_FILENAME,
        panda,
    )
    gate_start = phi_start - 0.5
    # Home the input encoder
    yield from bps.abs_set(
        panda.inenc[1].setp,  # type: ignore
        gate_start * DEG_TO_ENC_COUNTS,
        group="panda-setup",
    )
    yield from setup_outenc_vals(panda)

    seq_table = generate_panda_seq_table(phi_start, phi_end, phi_steps, exposure_time)

    yield from bps.abs_set(panda.seq[1].table, seq_table, group="panda-setup")

    # Values need to be set before blocks are enabled, so wait here
    yield from bps.wait(group="panda-setup", timeout=GENERAL_TIMEOUT)

    LOGGER.info(f"PandA sequencer table has been set to: {str(seq_table)}")
    seq_table_readback = yield from bps.rd(panda.seq[1].table)
    LOGGER.debug(f"PandA sequencer table readback is: {str(seq_table_readback)}")

    yield from arm_panda(panda)


def reset_panda(panda: HDFPanda, group="reset_panda"):
    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_THROUGH_ZEBRA,
        panda,
    )
    yield from bps.abs_set(panda.outenc[1].val, "INENC1.VAL", group=group)  # type: ignore
    yield from bps.abs_set(panda.outenc[2].val, "INENC2.VAL", group=group)  # type: ignore
