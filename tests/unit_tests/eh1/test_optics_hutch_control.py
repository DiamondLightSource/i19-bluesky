from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.i19.access_controlled.shutter import AccessControlledShutter

from i19_bluesky.eh1 import (
    close_experiment_shutter,
    open_experiment_shutter,
)
from i19_bluesky.plans.optics_hutch_control_plans import (
    apply_voltage_to_piezo_actuators,
)


@patch("i19_bluesky.plans.optics_hutch_control_plans.bps.abs_set")
async def test_open_shutter_plan(
    mock_set: MagicMock, eh1_shutter: AccessControlledShutter, RE: RunEngine
):
    RE(open_experiment_shutter(eh1_shutter))

    mock_set.assert_called_once_with(eh1_shutter, ShutterDemand.OPEN, wait=True)


@patch("i19_bluesky.plans.optics_hutch_control_plans.bps.abs_set")
async def test_close_shutter_plan(
    mock_set: MagicMock, eh1_shutter: AccessControlledShutter, RE: RunEngine
):
    RE(close_experiment_shutter(eh1_shutter))

    mock_set.assert_called_once_with(eh1_shutter, ShutterDemand.CLOSE, wait=True)


@patch("i19_bluesky.plans.optics_hutch_control_plans.bps.abs_set")
def test_apply_voltage_to_hfm_piezo_actuator(
    mock_set: MagicMock, eh1_hfm_piezo: AccessControlledPiezoActuator, RE: RunEngine
):
    RE(apply_voltage_to_piezo_actuators(3.2, eh1_hfm_piezo))
    mock_set.assert_called_once_with(eh1_hfm_piezo, 3.2, wait=True)


@patch("i19_bluesky.plans.optics_hutch_control_plans.bps.abs_set")
def test_apply_voltage_to_vfm_piezo_actuator(
    mock_set: MagicMock, eh1_vfm_piezo: AccessControlledPiezoActuator, RE: RunEngine
):
    RE(apply_voltage_to_piezo_actuators(1.42, eh1_vfm_piezo))
    mock_set.assert_called_once_with(eh1_vfm_piezo, 1.42, wait=True)
