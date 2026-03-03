import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo

from i19_bluesky.log import LOGGER
from i19_bluesky.optics.check_access_control import check_access


@check_access
def apply_voltage_to_piezo(
    voltage_demand: float, focus_mirror: FocusingMirrorWithPiezo
) -> MsgGenerator:
    LOGGER.info(f"Set {focus_mirror.name} piezo to {voltage_demand} V")
    yield from bps.abs_set(focus_mirror.piezo, voltage_demand, wait=True)
