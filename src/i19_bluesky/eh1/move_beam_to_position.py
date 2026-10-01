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
VFM_LUT = Path(
    "/dls_sw/i19-1/software/daq_configuration/lookup/vfm_nudge_to_position.txt"
)  # This one is a bit more complete as has both directions

TIME_TO_SETTLE = 2.0
TOLERANCE = 5.0
MAX_TRIES = 10


def _read_current_position(
    beam_centre: CentroidFromEpics,
) -> Generator[Msg, None, tuple[float, float]]:
    x = yield from bps.rd(beam_centre.beam_centre_x)
    y = yield from bps.rd(beam_centre.beam_centre_y)
    return (x, y)
    # return (x, y * 4 / 3)


# TODO Create model in daq-config-server
def _read_lut() -> list[list[float]]:
    config_client = get_config_client()
    lut_contents = config_client.get_file_contents(HFM_LUT.as_posix())
    lut = GenericLookupTable.from_contents(
        lut_contents, ("nudge", float), ("delta_x", float), ("delta_y", float)
    )
    # Column0: nudge, column1: x, column2: y
    return lut.columns


def _calculate_nudge_from_lut(distance: float) -> float:
    """Read lookup table and extract the voltage needed to get to that position.
    For now assume linear."""
    LOGGER.debug("Reading lut for nudge size...")
    lut_columns = _read_lut()

    interp_nudge = linear_interpolation_lut(lut_columns[1], lut_columns[0])
    nudge_size = interp_nudge(distance)
    return nudge_size


def nudge_hfm_and_move_beam_to_position(
    target_xy: tuple[float, float],
    # target_x: float,
    # start_x_pos: float,
    piezo_device: AccessControlledPiezoActuator = inject("hfm_piezo"),
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    """Given a known target position, nudge the piezo actuator to move the beam there.
    Current beam position is extracted from epics setting up the ad-plugin chain.
    Using only hfm for now to avoid issues with vfm not being in a closed loop.
    """
    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)

    # for _ in range(3):
    current_xy = yield from _read_current_position(beam_centre)
    LOGGER.info(f"Starting position: {current_xy}, position to reach: {target_xy}")
    current_voltage = yield from bps.rd(piezo_device.setpoint)

    # Should do in a loop until close enough
    # while True:
    delta_x = target_xy[0] - current_xy[0]
    i = 0
    while abs(delta_x) > TOLERANCE and i < MAX_TRIES:
        LOGGER.info(f"Loop {i + 1}")
        nudge_size = _calculate_nudge_from_lut(delta_x)
        LOGGER.info(
            f"Calculated hfm nudge for {delta_x}px move in x direction: {nudge_size}V"
        )

        current_voltage += nudge_size
        LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
        yield from apply_voltage_to_piezo_actuators(current_voltage, piezo_device)

        # For now just sleep for half a second to wait for settling
        LOGGER.info(f"Wait {TIME_TO_SETTLE}s to settle")
        yield from bps.sleep(TIME_TO_SETTLE)

        current_xy = yield from _read_current_position(beam_centre)
        LOGGER.info(f"Beam position after nudge: {current_xy}")
        delta_x = target_xy[0] - current_xy[0]
        i += 1
    # Then need to check if it's close enough in which case, break.


def nudge_vfm_and_move_beam_to_position(
    # target_y: float,
    # start_y_pos: float,
    target_xy: tuple[float, float],
    piezo_device: AccessControlledPiezoActuator = inject("vfm_piezo"),
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    """Given a known target position, nudge the piezo actuator to move the beam there.
    Current beam position is extracted from epics setting up the ad-plugin chain.
    Using only hfm for now to avoid issues with vfm not being in a closed loop.
    """
    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)

    # for _ in range(3):
    current_xy = yield from _read_current_position(beam_centre)
    LOGGER.info(f"Starting position: {current_xy}, position to reach: {target_xy}")
    current_voltage = yield from bps.rd(piezo_device.setpoint)

    # Should do in a loop until close enough
    # while True:
    delta_y = target_xy[1] - (
        current_xy[1] * 4 / 3
    )  # May be better to just do * 4 / 3 right at the start
    i = 0
    while abs(delta_y) > TOLERANCE and i < MAX_TRIES:
        LOGGER.info(f"Loop {i + 1}")
        dir = 1 if delta_y >= 0 else -1
        LOGGER.warning(f"DIRECTION: {dir}")
        nudge_size = _calculate_nudge_from_lut(delta_y)  # * dir
        LOGGER.info(
            f"Calculated vfm nudge for {delta_y}px move in y direction: {nudge_size}V"
        )
        if abs(nudge_size) >= 0.05:
            nudge_size = nudge_size / 2

        current_voltage += nudge_size
        LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
        yield from apply_voltage_to_piezo_actuators(current_voltage, piezo_device)

        # For now just sleep for half a second to wait for settling
        LOGGER.info(f"Wait {TIME_TO_SETTLE}s to settle")
        yield from bps.sleep(TIME_TO_SETTLE)

        current_xy = yield from _read_current_position(beam_centre)
        LOGGER.info(f"Beam position after nudge: {current_xy}")
        delta_y = target_xy[1] - (current_xy[1] * 4 / 3)
        i += 1


# Then need to check if it's close enough in which case, break.


def _check_position_reached(
    target_xy: tuple[float, float], current_xy: tuple[float, float]
) -> bool:
    _x = target_xy[0] - current_xy[0]
    _y = target_xy[1] - (current_xy[1] * 4 / 3)
    # For the checvk it does not need conversion anymore
    if abs(_x) <= 0.5 and abs(_y) <= 1.0:
        return True
    return False


def nudge_piezos_and_move_to_beam_centre(
    target_xy: tuple[float, float],
    hfm_piezo: AccessControlledPiezoActuator = inject("hfm_piezo"),
    vfm_piezo: AccessControlledPiezoActuator = inject("vfm_piezo"),
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)

    target_xy = (
        target_xy[0],
        target_xy[1] * 4 / 3,
    )  # beacue GDA is I put in crosshair from file

    current_xy = yield from _read_current_position(beam_centre)
    LOGGER.info(f"Starting position: {current_xy}, position to reach: {target_xy}")

    num = 0
    while num < MAX_TRIES:  # Should do something with tolerance here too but for later
        LOGGER.info(f"LOOP {num}")
        LOGGER.warning("Start from vfm")
        current_vfm_v = yield from bps.rd(vfm_piezo.setpoint)
        delta_y = target_xy[1] - current_xy[1]
        vfm_nudge_size = _calculate_nudge_from_lut(delta_y)
        LOGGER.info(
            f"Calculated vfm nudge for {delta_y}px move in y direction: {vfm_nudge_size}V"
        )

        current_vfm_v += vfm_nudge_size
        LOGGER.info(f"Apply {current_vfm_v} to {vfm_piezo.name}")
        yield from apply_voltage_to_piezo_actuators(current_vfm_v, vfm_piezo)

        LOGGER.info(f"Wait {TIME_TO_SETTLE}s for vfm to settle")
        yield from bps.sleep(TIME_TO_SETTLE)

        LOGGER.warning("Now hfm")
        current_hfm_v = yield from bps.rd(hfm_piezo.setpoint)
        delta_x = target_xy[0] - current_xy[0]
        hfm_nudge_size = _calculate_nudge_from_lut(delta_x)
        LOGGER.info(
            f"Calculated hfm nudge for {delta_x}px move in x direction: {hfm_nudge_size}V"
        )

        current_hfm_v += hfm_nudge_size
        LOGGER.info(f"Apply {current_hfm_v} to {hfm_piezo.name}")
        yield from apply_voltage_to_piezo_actuators(current_hfm_v, hfm_piezo)

        LOGGER.info(f"Wait {TIME_TO_SETTLE}s for hfm to settle")
        yield from bps.sleep(TIME_TO_SETTLE)

        current_xy = yield from _read_current_position(beam_centre)
        LOGGER.info(f"Beam position after nudge: {current_xy}")
        num += 1

        if _check_position_reached(target_xy, current_xy):
            break
    LOGGER.warning("DONE!")


#     LOGGER.warning("Start hfm nudge")
#     yield from nudge_hfm_and_move_beam_to_position(
#         target_xy[0], current_xy[0], hfm_piezo, beam_centre
#     )
#     # TODO NEED to do this properly as like this it doesn't wait for one plan to be
#     # done before starting the next. For time reason, doing the test manually on
#     # beamline for now
#     LOGGER.warning("Start vfm nudge")
#     yield from nudge_vfm_and_move_beam_to_position(
#         target_xy[1], current_xy[1], vfm_piezo, beam_centre
#     )

#     final_position = yield _read_current_position(beam_centre)
#     LOGGER.info(
#         f"DONE! Position reached: ({final_position[0]}, {final_position[1] * 3 / 4})"
#     )
