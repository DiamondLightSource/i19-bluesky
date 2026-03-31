import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.eh2.backlight_plan import move_backlight_in
from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


def move_backlight_in_via_ui(
    devices: DeviceInput = inject(""),
) -> MsgGenerator:
    yield from move_detector_stage(devices.diffractometer.det_stage, 250, 90)
    yield from move_backlight_in(devices.backlight)


def move_backlight_in_via_ui_quick(
    devices: DeviceInput = inject(""),
) -> MsgGenerator:
    yield from move_detector_stage(devices.diffractometer.det_stage, 100, 0)
    yield from move_backlight_in(devices.backlight)


def rotate_in_phi(
    parameters: SerialExperiment, devices: DeviceInput = inject("")
) -> MsgGenerator:
    parameters.rot_axis_start = yield from bps.rd(
        devices.diffractometer.phi.user_readback
    )
    parameters.rot_axis_end = parameters.rot_axis_increment + parameters.rot_axis_start
    yield from bps.abs_set(
        devices.diffractometer.phi, parameters.rot_axis_end, wait=True
    )
