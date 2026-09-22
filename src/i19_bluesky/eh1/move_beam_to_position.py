import bluesky.plan_stubs as bps
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
    ColourMode,
)


def _setup_ad_plugin_chain(
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
