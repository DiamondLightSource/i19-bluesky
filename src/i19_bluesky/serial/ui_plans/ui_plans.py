import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.eh2.backlight_plan import move_backlight_in
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


def move_backlight_in_via_ui(
    devices: SerialCollectionEh2PandaComposite = inject(""),
) -> MsgGenerator:
    yield from move_detector_stage(devices.diffractometer.det_stage, 250, 90)
    yield from move_backlight_in(devices.backlight)


def move_backlight_in_via_ui_quick(
    devices: SerialCollectionEh2PandaComposite = inject(""),
) -> MsgGenerator:
    yield from move_detector_stage(devices.diffractometer.det_stage, 100, 0)
    yield from move_backlight_in(devices.backlight)


def rotate_in_phi(
    parameters: dict,
    devices: SerialCollectionEh2PandaComposite = inject(""),
) -> MsgGenerator:
    rot_axis_start = yield from bps.rd(devices.diffractometer.phi.user_readback)
    rot_axis_end = parameters["rot_axis_increment"] + rot_axis_start
    yield from bps.abs_set(devices.diffractometer.phi, rot_axis_end, wait=True)
