import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.oav.beam_centre.beam_centre import CentreEllipseMethod

from i19_bluesky.log import LOGGER


def find_beam_centre_plan(
    beam_centre: CentreEllipseMethod = inject("beam_centre"),
) -> MsgGenerator:
    yield from bps.abs_set(
        beam_centre.roi_box_size, 10000
    )  # set it to something much bigger than needed so it will get fullscreen size
    LOGGER.info("Finding beam centre with roi_box_size set to 10000")
    yield from bps.trigger(beam_centre)
