from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.core import get_mock_put

from i19_bluesky.serial.example_trigger_plan_zebra_vs_panda import (
    abort_zebra,
    trigger_zebra,
)


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_zebra")
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.arm_zebra")
@patch(
    "i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_zebra_for_collection"
)
@patch("i19_bluesky.serial.run_serial_with_panda.setup_diffractometer")
async def test_trigger_zebra(
    mock_setup_diffractometer: MagicMock,
    mock_setup_zebra_for_collection: MagicMock,
    mock_arm_zebra: MagicMock,
    mock_disarm_zebra: MagicMock,
    eh2_zebra: Zebra,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
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
            zebra=eh2_zebra,
            diffractometer=eh2_diffractometer,
            phi_start=5,
            phi_end=10,
            phi_steps=25,
            exposure_time=10,
            gate_width=2,
            pulse_width=2,
        )
    )
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_has_calls([call(10), call(5)])

    expected_calls = [
        call.mock_setup_diffractometer(eh2_diffractometer, 4.5, 25, 10),
        call.mock_setup_diffractometer().__iter__(),
        call.mock_setup_zebra_for_collection(
            eh2_zebra, RotationDirection.POSITIVE, 4.5, 2, 2
        ),
        call.mock_setup_zebra_for_collection().__iter__(),
        call.mock_arm_zebra(eh2_zebra),
        call.mock_arm_zebra().__iter__(),
        call.mock_disarm_zebra(eh2_zebra),
        call.mock_disarm_zebra().__iter__(),
        call.mock_setup_diffractometer(eh2_diffractometer, 10.5, 25, 10),
        call.mock_setup_diffractometer().__iter__(),
        call.mock_setup_zebra_for_collection(
            eh2_zebra, RotationDirection.NEGATIVE, 4.5, 2, 2
        ),
        call.mock_setup_zebra_for_collection().__iter__(),
        call.mock_arm_zebra(eh2_zebra),
        call.mock_arm_zebra().__iter__(),
        call.mock_disarm_zebra(eh2_zebra),
        call.mock_disarm_zebra().__iter__(),
    ]

    parent_mock.assert_has_calls(expected_calls)


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_zebra")
async def test_abort_zebra(
    mock_disarm_zebra: MagicMock,
    eh2_zebra: Zebra,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(abort_zebra(eh2_diffractometer, eh2_zebra))
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_zebra.assert_called_once_with(eh2_zebra)
