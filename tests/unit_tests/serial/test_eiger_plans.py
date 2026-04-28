from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import DetectorTrigger, TriggerInfo
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.parameters.serial_parameters import PandaRotationParams
from i19_bluesky.serial.eiger_plans import (
    abort_simple_run,
    end_simple_run,
    loop_plan_for_testing,
    run_eiger,
    run_small_plan,
    setup_small_plan,
)


@patch("i19_bluesky.serial.eiger_plans.bps.unstage")
@patch("i19_bluesky.serial.eiger_plans.move_sample_stage_back")
@patch("i19_bluesky.serial.eiger_plans.reset_panda")
@patch("i19_bluesky.serial.eiger_plans.disarm_panda")
async def test_end_simple_run(
    mock_disarm_panda: MagicMock,
    mock_reset_panda: MagicMock,
    mock_move_sample_stage_back: MagicMock,
    mock_unstage_eiger: MagicMock,
    panda_rotation_params: PandaRotationParams,
    serial_stages: XYZPhiStage,
    mock_panda: HDFPanda,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        end_simple_run(
            panda_rotation_params.scan_start_deg,
            serial_stages,
            mock_panda,
            eh2_eiger,
        )
    )
    mock_unstage_eiger.assert_called_once_with(eh2_eiger)
    mock_move_sample_stage_back.assert_called_once_with(serial_stages, 0)
    mock_disarm_panda.assert_called_once_with(mock_panda)
    mock_reset_panda.assert_called_once_with(mock_panda)


@patch("i19_bluesky.serial.eiger_plans.bps.unstage")
@patch("i19_bluesky.serial.eiger_plans.bps.trigger")
@patch("i19_bluesky.serial.eiger_plans.bps.abs_set")
@patch("i19_bluesky.serial.eiger_plans.disarm_panda")
async def test_abort_simple_run(
    mock_disarm_panda: MagicMock,
    mock_abs_set: MagicMock,
    mock_bps_trigger: MagicMock,
    mock_unstage_eiger: MagicMock,
    eh2_diffractometer: FourCircleDiffractometer,
    mock_panda: HDFPanda,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(abort_simple_run(eh2_diffractometer, mock_panda, eh2_eiger))
    mock_unstage_eiger.assert_called_once_with(eh2_eiger)
    mock_disarm_panda.assert_called_once_with(mock_panda)
    mock_bps_trigger.assert_called_once_with(eh2_eiger.drv.detector.disarm)
    mock_abs_set.assert_called_once_with(
        eh2_diffractometer.phi.motor_stop, 1, wait=True
    )


@patch("i19_bluesky.serial.eiger_plans.bps.prepare")
@patch("i19_bluesky.serial.eiger_plans.setup_sample_stage")
@patch("i19_bluesky.serial.eiger_plans.setup_panda_for_rotation")
@patch("i19_bluesky.serial.eiger_plans.bps.stage")
def test_setup_small_plan(
    mock_bps_stage: MagicMock,
    mock_setup_panda_for_rotation: MagicMock,
    mock_setup_sample_stage: MagicMock,
    mock_bps_prepare: MagicMock,
    panda_rotation_params: PandaRotationParams,
    eh2_eiger: EigerDetector,
    mock_panda: HDFPanda,
    serial_stages: XYZPhiStage,
    RE: RunEngine,
):
    RE(setup_small_plan(panda_rotation_params, eh2_eiger, mock_panda, serial_stages))
    mock_bps_stage.assert_called_once_with(eh2_eiger)
    mock_setup_panda_for_rotation.assert_called_once_with(
        panda_rotation_params, mock_panda
    )
    mock_setup_sample_stage(panda_rotation_params, serial_stages)
    mock_bps_prepare.assert_called_once_with(
        eh2_eiger,
        TriggerInfo(
            number_of_events=1, trigger=DetectorTrigger.INTERNAL, deadtime=0.0001
        ),
        wait=True,
    )


@patch("i19_bluesky.serial.eiger_plans.bps.complete")
@patch("i19_bluesky.serial.eiger_plans.bps.abs_set")
@patch("i19_bluesky.serial.eiger_plans.bps.kickoff")
@pytest.mark.parametrize("well_num,phival", [(1, 0), (2, 1)])
def test_loop_plan_for_testing(
    mock_bps_kickoff: MagicMock,
    mock_abs_set: MagicMock,
    mock_bps_complete: MagicMock,
    panda_rotation_params: PandaRotationParams,
    eh2_eiger: EigerDetector,
    eh2_diffractometer: FourCircleDiffractometer,
    well_num: int,
    phival: float,
    RE: RunEngine,
):
    RE(
        loop_plan_for_testing(
            panda_rotation_params, eh2_eiger, eh2_diffractometer, well_num
        )
    )
    mock_bps_kickoff.assert_called_once_with(eh2_eiger, wait=True)
    mock_abs_set.assert_called_once_with(
        eh2_diffractometer.phi,
        phival,
        wait=True,
    )
    mock_bps_complete.assert_called_once_with(eh2_eiger, wait=True)


@patch("i19_bluesky.serial.eiger_plans.bps.abs_set")
@patch("i19_bluesky.serial.eiger_plans.bps.complete")
@patch("i19_bluesky.serial.eiger_plans.bps.kickoff")
@patch("i19_bluesky.serial.eiger_plans.move_stage_x_and_z")
@pytest.mark.parametrize(
    "well_position,well_num", [({1: [1, 2, 3]}, 1), ({2: [1, 2, 3]}, 2)]
)
def test_run_eiger(
    mock_move_stage_x_and_z: MagicMock,
    mock_bps_kickoff: MagicMock,
    mock_bps_complete: MagicMock,
    mock_bps_abs_set: MagicMock,
    well_position: dict,
    well_num: int,
    panda_rotation_params: PandaRotationParams,
    eh2_eiger: EigerDetector,
    serial_stages: XYZPhiStage,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(
        run_eiger(
            well_position,
            panda_rotation_params,
            eh2_eiger,
            serial_stages,
            eh2_diffractometer,
        )
    )
    mock_move_stage_x_and_z.assert_called_once_with(1, 3, serial_stages)
    if well_num % 2 == 0:
        mock_bps_abs_set.assert_called_once_with(
            eh2_diffractometer.phi,
            panda_rotation_params.scan_end_deg,
            wait=True,
        )
    else:
        mock_bps_abs_set.assert_called_once_with(
            eh2_diffractometer.phi,
            panda_rotation_params.scan_start_deg,
            wait=True,
        )


@patch("i19_bluesky.serial.eiger_plans.run_eiger")
@patch("i19_bluesky.serial.eiger_plans.setup_small_plan")
@pytest.mark.parametrize("well_position", [({1: [1, 2, 3]}), ({2: [1, 2, 3]})])
def test_run_small_plan(
    mock_setup_small_plan: MagicMock,
    mock_run_eiger: MagicMock,
    panda_rotation_params: PandaRotationParams,
    well_position: dict,
    eh2_eiger: EigerDetector,
    mock_panda: HDFPanda,
    serial_stages: XYZPhiStage,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(
        run_small_plan(
            panda_rotation_params,
            well_position,
            eh2_eiger,
            mock_panda,
            serial_stages,
            eh2_diffractometer,
        )
    )
    mock_setup_small_plan.assert_called_once_with(
        panda_rotation_params, eh2_eiger, mock_panda, serial_stages
    )
    mock_run_eiger.assert_called_once_with(
        well_position,
        panda_rotation_params,
        eh2_eiger,
        serial_stages,
        eh2_diffractometer,
    )
