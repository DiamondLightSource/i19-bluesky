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
    nudge_hfm_piezo_actuators,
    nudge_vfm_piezo_actuators,
    set_requested_voltage_to_hfm_piezo,
    set_requested_voltage_to_vfm_piezo,
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


@patch("i19_bluesky.plans.optics_hutch_control_plans.apply_voltage_to_piezo_actuators")
def test_set_requested_voltage_to_vfm(
    mock_apply_plan: MagicMock,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    RE(set_requested_voltage_to_vfm_piezo(1.42, eh1_vfm_piezo))
    mock_apply_plan.assert_called_once_with(1.42, eh1_vfm_piezo)


@patch("i19_bluesky.plans.optics_hutch_control_plans.apply_voltage_to_piezo_actuators")
def test_set_requested_voltage_to_hfm(
    mock_apply_plan: MagicMock,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    RE(set_requested_voltage_to_hfm_piezo(1.42, eh1_hfm_piezo))
    mock_apply_plan.assert_called_once_with(1.42, eh1_hfm_piezo)


@patch("i19_bluesky.plans.optics_hutch_control_plans.apply_voltage_to_piezo_actuators")
async def test_nudge_vfm_piezos(
    mock_apply_plan: MagicMock,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    assert await eh1_vfm_piezo.readback.get_value() == 0.849
    RE(nudge_vfm_piezo_actuators(0.005, eh1_vfm_piezo))
    mock_apply_plan.assert_called_once_with(0.854, eh1_vfm_piezo)


@patch("i19_bluesky.plans.optics_hutch_control_plans.apply_voltage_to_piezo_actuators")
async def test_nudge_hfm_piezos(
    mock_apply_plan: MagicMock,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    assert await eh1_hfm_piezo.readback.get_value() == 5.236
    RE(nudge_hfm_piezo_actuators(0.005, eh1_hfm_piezo))
    mock_apply_plan.assert_called_once_with(5.241, eh1_hfm_piezo)
