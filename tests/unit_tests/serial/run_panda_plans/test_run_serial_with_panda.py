from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.run_serial_with_panda import (
    main_collection_plan,
    run_serial_with_panda,
)


@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.end_run")
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.main_collection_plan")
async def test_run_serial_with_panda(
    mock_main_plan: MagicMock,
    mock_end_run: MagicMock,
    RE: RunEngine,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
):
    RE(run_serial_with_panda(parameters, devices))
    mock_main_plan.assert_called_once()
    mock_end_run.assert_called_once_with(
        parameters.rot_axis_start,
        devices.panda,
        devices.eiger,
        devices.serial_stages,
    )


@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.setup_eh2_serial_collection"
)
@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.trigger_panda_collection"
)
async def test_main_collection_plan(
    mock_trigger_panda: MagicMock,
    mock_setup_collection: MagicMock,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
):

    RE(main_collection_plan(parameters, devices))
    mock_setup_collection.assert_called_once_with(parameters, devices)
    mock_trigger_panda.assert_called_once_with(parameters, devices)
