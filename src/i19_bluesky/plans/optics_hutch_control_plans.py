"""Entry point plans that use access controlled devices to operate the optics
from one of the hutches."""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.i19.access_controlled.shutter import AccessControlledShutter

from i19_bluesky.log import LOGGER


def open_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to open the shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.OPEN, wait=True)


def close_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to close the shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.CLOSE, wait=True)


def apply_voltage_to_piezo_actuators(
    requested_voltage: float, piezo_device: AccessControlledPiezoActuator
) -> MsgGenerator[None]:
    LOGGER.info(f"Applying {requested_voltage} to {piezo_device.name}")
    yield from bps.abs_set(piezo_device, requested_voltage, wait=True)


def set_requested_voltage_to_hfm_piezo(
    requested_voltage: float,
    hfm_piezo: AccessControlledPiezoActuator = inject("hfm_piezo"),
) -> MsgGenerator[None]:
    yield from apply_voltage_to_piezo_actuators(requested_voltage, hfm_piezo)


def set_requested_voltage_to_vfm_piezo(
    requested_voltage: float,
    vfm_piezo: AccessControlledPiezoActuator = inject("vfm_piezo"),
) -> MsgGenerator[None]:
    yield from apply_voltage_to_piezo_actuators(requested_voltage, vfm_piezo)
