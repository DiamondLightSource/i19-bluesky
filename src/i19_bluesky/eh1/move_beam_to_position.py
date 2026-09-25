from collections.abc import Generator
from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import Msg, MsgGenerator
from daq_config_server.models.lookup_tables import GenericLookupTable
from dodal.common import inject
from dodal.common.beamlines.beamline_utils import (
    get_config_client,
)
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
)
from dodal.devices.util.lookup_tables import linear_interpolation_lut

from i19_bluesky.eh1.find_beam_centre import setup_ad_plugin_chain_for_beam_centre
from i19_bluesky.log import LOGGER
from i19_bluesky.plans.optics_hutch_control_plans import (
    apply_voltage_to_piezo_actuators,
)

HFM_LUT = Path(
    "/dls_sw/i19-1/software/daq_configuration/lookup/hfm_nudge_to_position_new.txt"
)  # This one is a bit more complete as has both directions


def _read_current_position(
    beam_centre: CentroidFromEpics,
) -> Generator[Msg, None, tuple[float, float]]:
    x = yield from bps.rd(beam_centre.beam_centre_x)
    y = yield from bps.rd(beam_centre.beam_centre_y)
    return (x, y)


# TODO Create model in daq-config-server
def _read_lut():
    config_client = get_config_client()
    lut_contents = config_client.get_file_contents(HFM_LUT.as_posix())
    lut = GenericLookupTable.from_contents(
        lut_contents, ("nudge", float), ("delta_x", float), ("delta_y", float)
    )
    # Column0: nudge, column1: x, column2: y
    return lut.columns


def _calculate_nudge_from_lut(distance: float) -> float:
    LOGGER.debug("Reading lut for nudge size...")
    lut_columns = _read_lut()

    interp_nudge = linear_interpolation_lut(lut_columns[1], lut_columns[0])
    nudge_size = interp_nudge(distance)
    return nudge_size


def nudge_hfm_and_move_beam_to_position(
    target_xy: tuple[float, float],
    piezo_device: AccessControlledPiezoActuator = inject("hfm_piezo"),
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)

    current_xy = yield from _read_current_position(beam_centre)
    current_voltage = yield from bps.rd(piezo_device.setpoint)

    delta_x = target_xy[0] - current_xy[0]
    nudge_size = _calculate_nudge_from_lut(delta_x)
    LOGGER.info(
        f"Calculated hfm nudge for {delta_x}px move in x direction: {nudge_size}V"
    )

    new_voltage = current_voltage + nudge_size
    LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
    yield from apply_voltage_to_piezo_actuators(new_voltage, piezo_device)

    current_xy = yield from _read_current_position(beam_centre)
    LOGGER.info(f"Beam position after nudge: {current_xy}")
