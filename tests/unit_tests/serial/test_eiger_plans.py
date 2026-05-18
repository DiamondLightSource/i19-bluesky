from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import DetectorTrigger, TriggerInfo
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.parameters.serial_parameters import (
    SerialExperimentEh2,
)
from i19_bluesky.serial.eiger_plans import (
    abort_simple_run,
    end_simple_run,
    setup_small_plan,
)


@patch("i19_bluesky.serial.eiger_plans.reset_panda")
@patch("i19_bluesky.serial.eiger_plans.move_sample_stage_back")
@patch("i19_bluesky.serial.eiger_plans.bps.unstage")
@patch("i19_bluesky.serial.eiger_plans.disarm_panda")
async def test_end_simple_run(
    mock_disarm_panda: MagicMock,
    mock_unstage_eiger: MagicMock,
    mock_move_sample_stage_back: MagicMock,
    mock_reset_panda: MagicMock,
    serial_stages: XYZPhiStage,
    mock_panda: HDFPanda,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        end_simple_run(
            0,
            serial_stages,
            mock_panda,
            eh2_eiger,
        )
    )
    mock_unstage_eiger.assert_called_once_with(eh2_eiger)
    mock_move_sample_stage_back.assert_called_once_with(serial_stages, 0)
    mock_disarm_panda.assert_called_once_with(mock_panda)
    mock_reset_panda.assert_called_once_with(mock_panda)


@patch("i19_bluesky.serial.eiger_plans.bps.trigger")
@patch("i19_bluesky.serial.eiger_plans.bps.abs_set")
@patch("i19_bluesky.serial.eiger_plans.bps.unstage")
@patch("i19_bluesky.serial.eiger_plans.disarm_panda")
async def test_abort_simple_run(
    mock_disarm_panda: MagicMock,
    mock_unstage_eiger: MagicMock,
    mock_abs_set: MagicMock,
    mock_trigger: MagicMock,
    eh2_diffractometer: FourCircleDiffractometer,
    mock_panda: HDFPanda,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        abort_simple_run(
            eh2_diffractometer,
            mock_panda,
            eh2_eiger,
        )
    )
    mock_unstage_eiger.assert_called_once_with(eh2_eiger)
    mock_disarm_panda.assert_called_once_with(mock_panda)
    mock_trigger.assert_called_once_with(eh2_eiger.detector.disarm)
    mock_abs_set.assert_called_once_with(
        eh2_diffractometer.phi.motor_stop, 1, wait=True
    )


@patch("i19_bluesky.serial.eiger_plans.bps.stage")
@patch("i19_bluesky.serial.eiger_plans.setup_panda_for_rotation")
@patch("i19_bluesky.serial.eiger_plans.setup_sample_stage")
@patch("i19_bluesky.serial.eiger_plans.bps.prepare")
def test_setup_small_plan(
    mock_bps_prepare: MagicMock,
    mock_setup_sample_stage: MagicMock,
    mock_setup_rotation: MagicMock,
    mock_bps_stage: MagicMock,
    parameters: SerialExperimentEh2,
    eh2_eiger: EigerDetector,
    mock_panda: HDFPanda,
    serial_stages: XYZPhiStage,
    RE: RunEngine,
):
    RE(
        setup_small_plan(
            parameters.panda_rotation_params,
            eh2_eiger,
            mock_panda,
            serial_stages,
        )
    )
    mock_bps_stage.assert_called_once_with(eh2_eiger)
    mock_setup_rotation.assert_called_once_with(
        parameters.panda_rotation_params, mock_panda
    )
    mock_setup_sample_stage(
        parameters.panda_rotation_params,
        serial_stages,
    )
    mock_bps_prepare(
        eh2_eiger,
        TriggerInfo(
            number_of_events=1, trigger=DetectorTrigger.INTERNAL, deadtime=0.0001
        ),
        wait=True,
    )
