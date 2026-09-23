import csv
import datetime
from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
)

from i19_bluesky.eh1.find_beam_centre import setup_ad_plugin_chain_for_beam_centre
from i19_bluesky.log import LOGGER
from i19_bluesky.plans.optics_hutch_control_plans import (
    apply_voltage_to_piezo_actuators,
)

SAVE_FILE_PATH = Path("/dls_sw/i19-1/software/bluesky/voltage_to_beam_position_data")
TIME_TO_SETTLE = 2


def _save_results_to_file(
    device_name: str,
    voltages: list[float],
    beam_positions_x: list[float],
    beam_positions_y: list[float],
    nudge_size: float,
):
    now = datetime.datetime.now()
    str_now = now.strftime("%H%M%S")
    filename = (
        SAVE_FILE_PATH
        / f"{str_now}_{device_name}_to_beam_centre_nudge_{nudge_size}.csv"
    )
    column_names = ["voltage", "beam position_x", "beam_position_y"]
    with open(filename, "w") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(column_names)
        writer.writerows(zip(voltages, beam_positions_x, beam_positions_y, strict=True))
    LOGGER.info(f"Data saved to {filename}")


def measure_piezo_voltages_vs_beam_position(
    num_steps: int,
    nudge_size: float,
    piezo_device: AccessControlledPiezoActuator,
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:

    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)

    current_voltage = yield from bps.rd(piezo_device.setpoint)

    nudges = [
        (80, 0.01),
        (40, 0.02),
        (20, 0.04),
        (10, 0.08),
    ]

    for num_steps, nudge_size in nudges:
        for _ in range(2):
            voltages = []
            beam_positions_x = []
            beam_positions_y = []
            for dir in [1, -1]:
                new_nudge_size = nudge_size * dir
                for _ in range(num_steps):
                    current_voltage += new_nudge_size  # type: ignore
                    LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
                    yield from apply_voltage_to_piezo_actuators(
                        current_voltage, piezo_device
                    )
                    # For now just sleep for half a second to wait for settling
                    LOGGER.info(f"Wait {TIME_TO_SETTLE}s to settle")
                    yield from bps.sleep(TIME_TO_SETTLE)
                    LOGGER.info("Find beam position")
                    beam_centre_x = yield from bps.rd(beam_centre.beam_centre_x)
                    beam_centre_y = yield from bps.rd(beam_centre.beam_centre_y)
                    LOGGER.info(f"Beam found at {beam_centre_x, beam_centre_y}")
                    voltages.append(current_voltage)
                    beam_positions_x.append(beam_centre_x)
                    beam_positions_y.append(beam_centre_y)
            _save_results_to_file(
                piezo_device.name,
                voltages,
                beam_positions_x,
                beam_positions_y,
                nudge_size,
            )
            yield from apply_voltage_to_piezo_actuators(
                current_voltage + nudge_size / 2, piezo_device
            )
