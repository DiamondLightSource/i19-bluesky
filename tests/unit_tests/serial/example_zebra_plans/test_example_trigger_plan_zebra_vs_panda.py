from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.core import get_mock_put

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2ZebraComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda import (
    abort_zebra,
    trigger_zebra,
)


@patch(
    "i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda.disarm_zebra"
)
@patch(
    "i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda.arm_zebra"
)
@patch(
    "i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda.setup_zebra_for_collection"
)
@patch(
    "i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda.setup_diffractometer"
)
async def test_trigger_zebra(
    mock_setup_diffractometer: MagicMock,
    mock_setup_zebra_for_collection: MagicMock,
    mock_arm_zebra: MagicMock,
    mock_disarm_zebra: MagicMock,
    RE: RunEngine,
    devices_zebra: SerialCollectionEh2ZebraComposite,
    parameters: SerialExperimentEh2,
):
    parent_mock = MagicMock()
    parent_mock.attach_mock(mock_setup_diffractometer, "mock_setup_diffractometer")
    parent_mock.attach_mock(
        mock_setup_zebra_for_collection, "mock_setup_zebra_for_collection"
    )
    parent_mock.attach_mock(mock_arm_zebra, "mock_arm_zebra")
    parent_mock.attach_mock(mock_disarm_zebra, "mock_disarm_zebra")
    RE(
        trigger_zebra(
            gate_width=2,
            pulse_width=2,
            parameters=parameters,
            devices=devices_zebra,
        )
    )
    mock_phi = get_mock_put(devices_zebra.diffractometer.phi.user_setpoint)
    mock_phi.assert_has_calls(
        [
            call(parameters.zebra_rotation_params.scan_end_deg),
            call(parameters.zebra_rotation_params.scan_start_deg),
        ]
    )

    expected_calls = [
        call.mock_setup_diffractometer(
            parameters.zebra_rotation_params, devices_zebra.diffractometer
        ),
        call.mock_setup_zebra_for_collection(
            devices_zebra.zebra,
            RotationDirection.POSITIVE,
            parameters.zebra_rotation_params.ramp_start,
            2,
            2,
        ),
        call.mock_arm_zebra(devices_zebra.zebra),
        call.mock_disarm_zebra(devices_zebra.zebra),
        call.mock_setup_diffractometer(
            parameters.zebra_rotation_params, devices_zebra.diffractometer
        ),
        call.mock_setup_zebra_for_collection(
            devices_zebra.zebra,
            RotationDirection.NEGATIVE,
            parameters.zebra_rotation_params.ramp_start,
            2,
            2,
        ),
        call.mock_arm_zebra(devices_zebra.zebra),
        call.mock_disarm_zebra(devices_zebra.zebra),
    ]

    parent_mock.assert_has_calls(expected_calls, any_order=True)


@patch(
    "i19_bluesky.serial.example_zebra_plans.example_trigger_plan_zebra_vs_panda.disarm_zebra"
)
async def test_abort_zebra(
    mock_disarm_zebra: MagicMock,
    eh2_zebra: Zebra,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(abort_zebra(eh2_diffractometer, eh2_zebra))
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_zebra.assert_called_once_with(eh2_zebra)
