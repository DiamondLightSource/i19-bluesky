from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
)

from i19_bluesky.eh1.find_beam_centre import setup_ad_plugin_chain_for_beam_centre


def move_beam_to_position(
    piezo_device: AccessControlledPiezoActuator,
    beam_centre: CentroidFromEpics = inject("beam_centre_from_epics"),
) -> MsgGenerator:
    yield from setup_ad_plugin_chain_for_beam_centre(beam_centre)
