"""
i19 PandA setup plan for serial collection.
"""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.plans.load_panda_yaml import load_panda_from_yaml
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.serial_parameters import SerialExperiment
from i19_bluesky.serial.panda_setup_plans.panda_stubs import (
    DeviceSettingsConstants,
    arm_panda,
    generate_panda_seq_table,
    setup_outenc_vals,
)

DEG_TO_ENC_COUNTS = 1000
GENERAL_TIMEOUT = 60


def setup_panda_for_rotation(
    parameters: SerialExperiment,
    panda: HDFPanda,
) -> MsgGenerator:
    """Configures the PandA device for phi forward and backward rotation

    Args:
        panda (HDFPanda): The fastcs PandA ophyd device.
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
    """

    yield from bps.stage(panda, group="panda-setup")

    yield from load_panda_from_yaml(
        DeviceSettingsConstants.PANDA_DIR.as_posix(),
        DeviceSettingsConstants.PANDA_PC_FILENAME,
        panda,
    )
    gate_start = parameters["rot_axis_start"] - 0.5
    # Home the input encoder
    yield from bps.abs_set(
        panda.inenc[1].setp,  # type: ignore
        gate_start * DEG_TO_ENC_COUNTS,
        group="panda-setup",
    )
    yield from setup_outenc_vals(panda)

    seq_table = generate_panda_seq_table(
        parameters["rot_axis_start"],
        parameters["rot_axis_end"],
        parameters["images_per_well"],
        parameters["exposure_time_s"],
    )

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
