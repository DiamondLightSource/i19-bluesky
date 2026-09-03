from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from ophyd_async.core import get_mock_put

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.run_serial_with_panda import (
    main_collection_plan,
    run_on_collection_abort,
    run_on_collection_end,
    run_serial_with_panda,
)


@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.run_on_collection_end")
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
        devices.shutter,
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


@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.bps.trigger")
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.disarm_panda")
async def test_run_on_collection_abort(
    mock_disarm_panda: MagicMock,
    mock_disarm_eiger: MagicMock,
    RE: RunEngine,
    devices: SerialCollectionEh2PandaComposite,
):
    RE(run_on_collection_abort(devices.panda, devices.eiger, devices.diffractometer))
    get_mock_put(devices.diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_eiger.assert_called_once_with(devices.eiger.detector.disarm)
    mock_disarm_panda.assert_called_once_with(devices.panda)


@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.close_experiment_shutter"
)
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.reset_panda")
@patch(
    "i19_bluesky.serial.run_panda_plans.run_serial_with_panda.move_sample_stage_back"
)
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.bps.trigger")
@patch("i19_bluesky.serial.run_panda_plans.run_serial_with_panda.disarm_panda")
async def test_end_run(
    mock_disarm_panda: MagicMock,
    mock_disarm_eiger: MagicMock,
    mock_move_sample_stage_back: MagicMock,
    mock_reset_panda: MagicMock,
    mock_close_shutter: MagicMock,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
    RE: RunEngine,
):
    RE(
        run_on_collection_end(
            parameters.rot_axis_start,
            devices.panda,
            devices.eiger,
            devices.serial_stages,
            devices.shutter,
        )
    )
    mock_disarm_eiger.assert_called_once_with(devices.eiger.detector.disarm)
    mock_move_sample_stage_back.assert_called_once_with(devices.serial_stages, 0)
    mock_disarm_panda.assert_called_once_with(devices.panda)
    mock_reset_panda.assert_called_once_with(devices.panda)
    mock_close_shutter.assert_called_once_with(devices.shutter)
