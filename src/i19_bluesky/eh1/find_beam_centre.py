from collections.abc import Generator

import bluesky.plan_stubs as bps
from bluesky.utils import Msg, MsgGenerator
from dodal.common import inject
from dodal.devices.oav.beam_centre.beam_centre import CentreEllipseMethod
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
    ColourMode,
)
from dodal.devices.oav.oav_detector import OAVBeamCentreFile

from i19_bluesky.log import LOGGER


def setup_ad_plugin_chain_for_beam_centre(
    beam_centre: CentroidFromEpics, group: str = "setup_plugin_chain", wait: bool = True
):
    # Set BL19I-EA-OAV-01:CC:NDArrayPort_RBV to OAV1.cam
    yield from bps.abs_set(beam_centre.cc_array_port, "OAV1.cam", group=group)
    # Set BL19I-EA-OAV-01:CC:ColorModeOut to Mono
    yield from bps.abs_set(beam_centre.colour_mode, ColourMode.MONO, group=group)
    # Set BL19I-EA-OAV-01:STAT:NDArrayPort_RBV to OAV1.cc
    yield from bps.abs_set(beam_centre.stat_array_port, "OAV1.cc", group=group)
    # Set BL19I-EA-OAV-01:STAT:CentroidThreshold to 20
    yield from bps.abs_set(beam_centre.centroid_threshold, 20, group=group)
    if wait:
        yield from bps.wait(group=group)


def trigger_beam_centre_fit(
    beam_centre: CentreEllipseMethod,
) -> Generator[Msg, None, tuple[float, float]]:
    yield from bps.trigger(beam_centre, wait=True)

    centre_x = yield from bps.rd(beam_centre.center_x_val)
    centre_y = yield from bps.rd(beam_centre.center_y_val)
    return centre_x, centre_y


def find_beam_centre_plan(
    beam_centre: CentreEllipseMethod = inject("beam_centre"),
    oav: OAVBeamCentreFile = inject("oav1"),
) -> MsgGenerator:
    # Read image size from PVs and set the ROI box to the greater one.
    x_size = yield from bps.rd(oav.snapshot.x_size)
    y_size = yield from bps.rd(oav.snapshot.y_size)
    roi_size = max(x_size, y_size)
    yield from bps.abs_set(beam_centre.roi_box_size, roi_size, wait=True)

    LOGGER.info(f"Finding beam centre with roi_box_size set to {roi_size}")
    centre_x, centre_y = yield from trigger_beam_centre_fit(beam_centre)
    return centre_x, centre_y
