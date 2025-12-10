import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo

from i19_bluesky.log import LOGGER
from i19_bluesky.optics.check_access_control import check_access


@check_access
def apply_voltage_to_vfm_piezo(
    demand: float, vfm: FocusingMirrorWithPiezo = inject("vfm")
) -> MsgGenerator:
    LOGGER.info("Set vfm piezo to {demand} V")
    yield from bps.abs_set(vfm.piezo, demand, wait=True)


@check_access
def apply_voltage_to_hfm_piezo(
    demand: float, hfm: FocusingMirrorWithPiezo = inject("hfm")
) -> MsgGenerator:
    LOGGER.info("Set hfm piezo to {demand} V")
    yield from bps.abs_set(hfm.piezo, demand, wait=True)
