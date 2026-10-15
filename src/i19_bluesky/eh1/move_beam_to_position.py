from collections.abc import Generator
from math import dist
from pathlib import Path

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import Msg, MsgGenerator
from daq_config_server.models.lookup_tables import GenericLookupTable
from dodal.common import inject
from dodal.common.beamlines.beamline_utils import (
    get_config_client,
)
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
    StrEnum,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
    CentroidSettings,
    ColourMode,
)
from dodal.devices.util.lookup_tables import linear_interpolation_lut

from i19_bluesky.log import LOGGER
from i19_bluesky.plans.optics_hutch_control_plans import (
    apply_voltage_to_piezo_actuators,
)

PLUGIN_SETTINGS = CentroidSettings(threshold=20, colour_mode=ColourMode.MONO)

HFM_LUT = Path(
    "/dls_sw/i19-1/software/daq_configuration/lookup/hfm_nudge_to_position.txt"
)
VFM_LUT = Path(
    "/dls_sw/i19-1/software/daq_configuration/lookup/vfm_nudge_to_position.txt"
)

TIME_TO_SETTLE = 2.0
TOLERANCE = 0.5
MAX_TRIES = 10


class NudgeDirection(StrEnum):
    X = "x"
    Y = "y"


def _read_current_position(
    beam_centre: CentroidFromEpics,
) -> Generator[Msg, None, tuple[float, float]]:
    x = yield from bps.rd(beam_centre.beam_centre_x)
    y = yield from bps.rd(beam_centre.beam_centre_y)
    return (x, y)


# Move to device once eh2 also has LUT
# See https://github.com/DiamondLightSource/dodal/issues/2236
# and https://github.com/DiamondLightSource/i19-bluesky/issues/188
def _read_lut(lut_path: Path) -> list[list[float]]:
    config_client = get_config_client()
    lut_contents = config_client.get_file_contents(lut_path.as_posix())
    lut = GenericLookupTable.from_contents(
        lut_contents, ("nudge", float), ("delta_x", float), ("delta_y", float)
    )
    # Column0: nudge, column1: x, column2: y
    return lut.columns


def _get_lut_path_and_column_from_name(device_name: str) -> tuple[Path, int]:
    match device_name:
        case "hfm_piezo":
            return (HFM_LUT, 1)
        case "vfm_piezo":
            return (VFM_LUT, 2)
        case _:
            raise ValueError("Unknown device name, please pass one of the piezos.")


def _calculate_nudge_from_lut(distance: float, device_name: str) -> float:
    """Read lookup table and extract the voltage needed to get to that position.
    From first tests linear seems a good approximation."""
    lut_path, column_idx = _get_lut_path_and_column_from_name(device_name)
    LOGGER.debug("Reading lut for nudge size...")
    lut_columns = _read_lut(lut_path)

    interp_nudge = linear_interpolation_lut(lut_columns[column_idx], lut_columns[0])
    nudge_size = interp_nudge(distance)
    return nudge_size


def _check_position_reached(
    target_xy: tuple[float, float], current_xy: tuple[float, float]
) -> bool:
    if dist(target_xy, current_xy) <= TOLERANCE:
        LOGGER.info("Position reached within tolerance.")
        return True
    return False


def nudge_single_piezo(delta_pos: float, piezo_device: AccessControlledPiezoActuator):
    current_voltage = yield from bps.rd(piezo_device.setpoint)
    LOGGER.debug(f"Current voltage before nudge: {current_voltage}")
    nudge_size = _calculate_nudge_from_lut(delta_pos, piezo_device.name)
    LOGGER.info(
        f"Calculated {piezo_device.name} nudge for {delta_pos}px move: {nudge_size}V"
    )
    current_voltage += nudge_size
    LOGGER.info(f"Apply {current_voltage} to {piezo_device.name}")
    yield from apply_voltage_to_piezo_actuators(current_voltage, piezo_device)


def nudge_piezos_and_move_to_beam_centre(
    target_xy: tuple[float, float],
    max_iterations: int = MAX_TRIES,
    hfm_piezo: AccessControlledPiezoActuator = inject("hfm_piezo"),
    vfm_piezo: AccessControlledPiezoActuator = inject("vfm_piezo"),
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    """Given a known target position, nudge the piezo actuators to move the beam there.
    Current beam position is extracted from epics setting up the ad-plugin chain.

    The hfm will move the beam in x while the vfm moves it in y. However, both actuators
    also slightly move the beam in the other direction upon being nudged. The change in
    y for the hfm is small enough to be ignored but the vfm may change x by 1 px (likely
    due to it not being in a closed loop). Therefore, the vfm is nudged first in order
    to make up for this shift when nudging the hfm.

    The target (x,y) position usually comes from the display.configuration and refers to
    the crosshair position in GDA (not the one on the OAV viewer). In this case, the
    conversion of the position is:
        x_centroid = x_crosshair
        y_centroid = y_crosshair * 4/3

    For now the conversion is done in the plan but it should really come from GDA so
    that we can use the same algorithm when not using it. Additionally, eh2 might have a
    different ratio they need.

    Args:
        target_xy: Position of the crosshair to centre the beam on, in px.
        max_iterations: Maximum number of iterations for the algorithm to run.
        hfm_piezo: Device controlling the piezo on the hfm.
        vfm_piezo: Device controlling the piezo on the vfm.
        beam_centre: Device to set up the AD plugin chain and read the centroid.
    """
    # NOTE. This is for eh1 only and the already converted value should just come from
    # GDA when that part is written
    target_xy = (
        target_xy[0],
        round(target_xy[1] * 4 / 3, 3),
    )  # beacuse GDA, the input value is that of the crosshair from file

    @bpp.stage_decorator([beam_centre])
    def run_loop():
        current_xy = yield from _read_current_position(beam_centre)
        LOGGER.info(f"Starting position: {current_xy}, position to reach: {target_xy}")
        yield from bps.prepare(beam_centre, PLUGIN_SETTINGS, wait=True)

        num = 0
        while not _check_position_reached(target_xy, current_xy):
            if num == max_iterations:
                LOGGER.warning("Maximum number of iterations reached, stopping loop.")
                break
            LOGGER.info("Start nudging vfm")
            delta_y = target_xy[1] - current_xy[1]
            yield from nudge_single_piezo(delta_y, vfm_piezo)

            LOGGER.info(f"Wait {TIME_TO_SETTLE}s for vfm to settle")
            yield from bps.sleep(TIME_TO_SETTLE)

            LOGGER.info("Now nudge hfm")
            delta_x = target_xy[0] - current_xy[0]
            yield from nudge_single_piezo(delta_x, hfm_piezo)

            LOGGER.info(f"Wait {TIME_TO_SETTLE}s for hfm to settle")
            yield from bps.sleep(TIME_TO_SETTLE)

            current_xy = yield from _read_current_position(beam_centre)
            LOGGER.info(f"Beam position after nudge: {current_xy}")
            num += 1
        LOGGER.info("DONE!")

    yield from run_loop()


# NOTE. The following plan may not be needed at all in the future but until further
# testing can be done it would be easier to have a separate entry point to test each
# piezo nudge in isolation.


def nudge_and_move_in_one_direction(
    target: float,
    direction: NudgeDirection,
    piezo_device: AccessControlledPiezoActuator,
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    """Given a known target position, nudge the single piezo actuator to move the beam
    towards it in just one direction - x for the hfm_piezo device and y for vfm_piezo.

    This plan should be used to test the beam move in each direction in isolation,
    keeping in mind that it will likely not bring the beam to the exact centre.
    """
    if direction is NudgeDirection.X:
        target_position = target
        beam_position = beam_centre.beam_centre_x
    else:
        target_position = round(target * 4 / 3, 3)
        beam_position = beam_centre.beam_centre_y

    @bpp.stage_decorator([beam_centre])
    def nudge_loop():
        yield from bps.prepare(beam_centre, PLUGIN_SETTINGS, wait=True)

        current_position = yield from bps.rd(beam_position)
        LOGGER.info(
            f"""
            Starting position: {current_position}, position to reach: {target_position},
            nudging {piezo_device.name} in {direction} direction.
            """
        )

        delta = target_position - current_position
        i = 0
        while abs(delta) > TOLERANCE:
            if i >= MAX_TRIES:
                break

            yield from nudge_single_piezo(delta, piezo_device)

            LOGGER.info(f"Wait {TIME_TO_SETTLE}s to settle")
            yield from bps.sleep(TIME_TO_SETTLE)

            current_position = yield from bps.rd(beam_position)
            LOGGER.info(f"Beam position after nudge: {current_position}")
            delta = target_position - current_position
            i += 1

    yield from nudge_loop()
