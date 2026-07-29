import csv
from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.beam_centre import CentreEllipseMethod
from dodal.devices.oav.oav_detector import OAVBeamCentreFile

from i19_bluesky.eh1.find_beam_centre import find_beam_centre_plan
from i19_bluesky.log import LOGGER
from i19_bluesky.plans.optics_hutch_control_plans import (
    apply_voltage_to_piezo_actuators,
)

SAVE_FILE_PATH = Path("/dls_sw/i19-1/software/blueaky")
TIME_TO_SETTLE = 0.5


def _save_results_to_file(
    device_name: str, voltages: list[float], beam_positions: list[tuple[float, float]]
):
    filename = SAVE_FILE_PATH / f"{device_name}_to_beam_centre.csv"
    column_names = ["voltage", "beam position"]
    with open(filename, "w") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(column_names)
        writer.writerows(zip(voltages, beam_positions, strict=True))
    LOGGER.info(f"Data saved to {filename}")


def measure_piezo_voltages_vs_beam_position(
    num_steps: int,
    nudge_size: float,
    piezo_device: AccessControlledPiezoActuator,
    beam_centre: CentreEllipseMethod = inject("beam_centre"),
    oav: OAVBeamCentreFile = inject("oav1"),
) -> MsgGenerator:
    voltages = []
    beam_positions = []
    current_voltage = yield from bps.rd(piezo_device.setpoint)

    for _ in range(num_steps):
        current_voltage += nudge_size  # type: ignore
        LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
        yield from apply_voltage_to_piezo_actuators(current_voltage, piezo_device)
        # For now just sleep for half a second to wait for settling
        LOGGER.info(f"Wait {TIME_TO_SETTLE}s to settle")
        yield from bps.sleep(TIME_TO_SETTLE)
        LOGGER.info("Find beam position")
        beam_centre = yield from find_beam_centre_plan(beam_centre, oav)
        LOGGER.info(f"Beam found at {beam_centre}")
        voltages.append(current_voltage)
        beam_positions.append(beam_centre)
    _save_results_to_file(piezo_device.name, voltages, beam_positions)
