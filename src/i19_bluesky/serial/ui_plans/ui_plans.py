from enum import StrEnum

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.motors import XYZPhiStage

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


def rotate_in_phi(
    rot_increment: float,
    serial_stages: XYZPhiStage = inject("serial_stages"),
) -> MsgGenerator:
    rot_axis_start = yield from bps.rd(serial_stages.phi.user_readback)
    rot_axis_end = rot_increment + rot_axis_start
    yield from bps.abs_set(serial_stages.phi, rot_axis_end, wait=True)
