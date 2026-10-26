"""
i19 PandA setup plan for serial collection.
"""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.motors import XYZPhiStage
from dodal.plans.load_panda_yaml import load_panda_from_yaml
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.components import PandaRotationParams
from i19_bluesky.serial.panda_plans.panda_stubs import (
    DEG_TO_ENC_COUNTS,
    DeviceSettingsConstants,
    arm_panda,
    generate_panda_seq_table,
)

GENERAL_TIMEOUT = 60

PANDA_SETUP_GRP = "panda-setup"


def setup_panda_for_rotation(
    parameters: PandaRotationParams,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
) -> MsgGenerator:
    """Configures the PandA device for phi forward and backward rotation

    Args:
        parameters (PandaRotationParams): PandaRotationParams object
        panda (HDFPanda): The fastcs PandA ophyd device.
    """

    yield from bps.stage(panda, group=PANDA_SETUP_GRP)

    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_SERIAL_FILENAME,
        panda,
    )
    LOGGER.info("Move phi to gate start position and home panda there")
    yield from bps.mv(serial_stages.phi, parameters.gate_start)
    gate_start = parameters.gate_start * DEG_TO_ENC_COUNTS
    LOGGER.info(f"Set inenc4 setp to {gate_start}")
    # Home the input encoder
    yield from bps.abs_set(
        panda.inenc[4].setp,  # type: ignore
        gate_start,
        group=PANDA_SETUP_GRP,
    )

    yield from bps.abs_set(
        panda.pulse[1].width, parameters.exposure_time_s, group=PANDA_SETUP_GRP
    )

    seq_table = generate_panda_seq_table(
        parameters.scan_start_deg,
        parameters.scan_end_deg,
        parameters.scan_steps,
        parameters.exposure_time_s,
    )

    yield from bps.abs_set(panda.seq[2].table, seq_table, group=PANDA_SETUP_GRP)

    # Values need to be set before blocks are enabled, so wait here
    yield from bps.wait(group=PANDA_SETUP_GRP, timeout=GENERAL_TIMEOUT)

    LOGGER.info(f"PandA sequencer table has been set to: {str(seq_table)}")
    seq_table_readback = yield from bps.rd(panda.seq[1].table)
    LOGGER.debug(f"PandA sequencer table readback is: {str(seq_table_readback)}")

    yield from arm_panda(panda)


def reset_panda(panda: HDFPanda):
    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_STANDARD_FILENAME,
        panda,
    )
