import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.eh2.backlight_plan import move_backlight_in
from i19_bluesky.parameters.components import BacklightOption
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


def move_backlight_in_via_ui(
    option: BacklightOption,
    devices: SerialCollectionEh2PandaComposite = inject(""),
) -> MsgGenerator:
    match option:
        case option.SLOW:
            det_z, two_theta = 250.0, 90.0
        case option.QUICK:
            det_z, two_theta = 100.0, 0.0
    yield from move_detector_stage(devices.diffractometer.det_stage, det_z, two_theta)
    yield from move_backlight_in(devices.backlight)


def rotate_in_phi(
    rot_increment: float,
    devices: SerialCollectionEh2PandaComposite = inject(""),
) -> MsgGenerator:
    rot_axis_start = yield from bps.rd(devices.diffractometer.phi.user_readback)
    rot_axis_end = rot_increment + rot_axis_start
    yield from bps.abs_set(devices.diffractometer.phi, rot_axis_end, wait=True)
