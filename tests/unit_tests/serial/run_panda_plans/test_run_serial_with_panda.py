from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine

from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.run_panda_plans.run_serial_with_panda import (
    run_serial_with_panda,
    setup_then_trigger_panda,
)


@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.end_run")
@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.setup_then_trigger_panda"
)
async def test_run_serial_with_panda(
    mock_setup_then_trigger_panda: MagicMock,
    mock_end_run: MagicMock,
    RE: RunEngine,
    parameters: SerialExperiment,
    devices: DeviceInput,
):
    RE(run_serial_with_panda(parameters, devices))
    mock_setup_then_trigger_panda.assert_called_once()
    mock_end_run.assert_called_once_with(parameters, devices)


@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.setup_beamline_before_collection"
)
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.trigger_panda")
async def test_setup_then_trigger_panda(
    mock_trigger_panda: MagicMock,
    mock_setup_beamline_before_collection: MagicMock,
    devices: DeviceInput,
    parameters: SerialExperiment,
    RE: RunEngine,
):
    RE(setup_then_trigger_panda(parameters, devices))
    mock_setup_beamline_before_collection.assert_called_once_with(parameters, devices)
    mock_trigger_panda.assert_called_once_with(parameters, devices)
