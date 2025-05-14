from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.shutter import AccessControlledShutter

from i19_bluesky.eh1 import (
    close_experiment_shutter,
    open_experiment_shutter,
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
