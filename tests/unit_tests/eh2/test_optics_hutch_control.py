from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.hutch_shutter import ShutterDemand
from dodal.devices.i19.shutter import AccessControlledShutter

from i19_bluesky.eh2.eh2_optics_hutch_control import (
    close_experiment_shutter,
    open_experiment_shutter,
)


@patch("i19_bluesky.eh1.eh1_optics_hutch_control.bps.abs_set")
async def test_open_shutter_plan(
    mock_set: MagicMock, eh2_shutter: AccessControlledShutter, RE: RunEngine
):
    RE(open_experiment_shutter(eh2_shutter))

    mock_set.assert_called_once_with(eh2_shutter, ShutterDemand.OPEN, wait=True)


@patch("i19_bluesky.eh1.eh1_optics_hutch_control.bps.abs_set")
async def test_close_shutter_plan(
    mock_set: MagicMock, eh2_shutter: AccessControlledShutter, RE: RunEngine
):
    RE(close_experiment_shutter(eh2_shutter))

    mock_set.assert_called_once_with(eh2_shutter, ShutterDemand.CLOSE, wait=True)
