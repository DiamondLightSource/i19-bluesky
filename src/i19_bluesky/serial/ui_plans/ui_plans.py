from enum import StrEnum

from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer

from i19_bluesky.eh2.backlight_plan import move_backlight_in
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


class BacklightOption(StrEnum):
    SLOW = "Slow"
    QUICK = "Quick"


def move_backlight_in_via_ui(
    option: BacklightOption,
    backlight: BacklightPosition = inject("backlight"),
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator:
    match option:
        case option.SLOW:
            det_z, two_theta = 250.0, 90.0
        case option.QUICK:
            det_z, two_theta = 100.0, 0.0
    yield from move_detector_stage(diffractometer.det_stage, det_z, two_theta)
    yield from move_backlight_in(backlight)
