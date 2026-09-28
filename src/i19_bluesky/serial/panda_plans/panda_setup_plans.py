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
    DeviceSettingsConstants,
    arm_panda,
    generate_panda_seq_table,
    setup_outenc_vals,
)

# DEG_TO_ENC_COUNTS = 1000
DEG_TO_ENC_COUNTS = -16667  # From Marks calculations... BUT sign is other way around.
GENERAL_TIMEOUT = 60


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

    yield from bps.stage(panda, group="panda-setup")

    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_SERIAL_CONFIG,
        panda,
    )
    LOGGER.warning(f"Gate start: {parameters.gate_start}")
    LOGGER.info("Move phi to gate start position and home panda there")
    yield from bps.mv(serial_stages.phi, parameters.gate_start)
    gate_start = parameters.gate_start * DEG_TO_ENC_COUNTS
    LOGGER.warning(f"Set inenc setp to {gate_start}")
    # Home the input encoder
    yield from bps.abs_set(
        panda.inenc[4].setp,  # type: ignore
        gate_start,
        wait=True,
        # group="panda-setup",
    )
    yield from setup_outenc_vals(panda)

    yield from bps.abs_set(
        panda.pulse[1].width, parameters.exposure_time_s, group="setup-panda"
    )

    seq_table = generate_panda_seq_table(
        parameters.scan_start_deg,
        parameters.scan_end_deg,
        parameters.scan_steps,
        parameters.exposure_time_s,
    )

    yield from bps.abs_set(panda.seq[1].table, seq_table, group="panda-setup")

    # Values need to be set before blocks are enabled, so wait here
    yield from bps.wait(group="panda-setup", timeout=GENERAL_TIMEOUT)

    LOGGER.info(f"PandA sequencer table has been set to: {str(seq_table)}")
    seq_table_readback = yield from bps.rd(panda.seq[1].table)
    LOGGER.debug(f"PandA sequencer table readback is: {str(seq_table_readback)}")

    yield from arm_panda(panda)


def reset_panda(panda: HDFPanda, group="reset_panda"):
    # NOTE. Beamline staff would like this called only when UI closes
    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_STANDARD_CONFIG,
        panda,
    )
    # Should go back to zebra settings
    yield from bps.abs_set(panda.outenc[1].val, "INENC1.VAL", group=group)  # type: ignore
    yield from bps.abs_set(panda.outenc[4].val, "INENC4.VAL", group=group)  # type: ignore
