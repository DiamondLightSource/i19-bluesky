from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.core import get_mock_put
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.example_trigger_plan_zebra_vs_panda import (
    abort_panda,
    abort_zebra,
    move_diffractometer_back,
    setup_diffractometer,
    trigger_panda,
    trigger_zebra,
)


async def test_setup_diffractometer(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_diffractometer(eh2_diffractometer, 6.0, 10, 2))
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_called_once_with(6.0, wait=True)

    mock_phi_velocity = get_mock_put(eh2_diffractometer.phi.velocity)
    mock_phi_velocity.assert_called_once_with(5.0, wait=True)


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_zebra")
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.arm_zebra")
@patch(
    "i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_zebra_for_collection"
)
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_diffractometer")
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
    mock_phi.assert_has_calls([call(10, wait=True), call(5, wait=True)])

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


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.reset_panda")
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.bps.sleep")
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_panda")
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.arm_panda")
@patch(
    "i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_panda_for_rotation"
)
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_diffractometer")
async def test_trigger_panda(
    mock_setup_diffractometer: MagicMock,
    mock_setup_panda_for_rotation: MagicMock,
    mock_arm_panda: MagicMock,
    mock_disarm_panda: MagicMock,
    mock_sleep: MagicMock,
    mock_reset_panda: MagicMock,
    mock_panda: HDFPanda,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    parent_mock = MagicMock()
    parent_mock.attach_mock(mock_setup_diffractometer, "mock_setup_diffractometer")
    parent_mock.attach_mock(
        mock_setup_panda_for_rotation, "mock_setup_panda_for_rotation"
    )
    parent_mock.attach_mock(mock_arm_panda, "mock_arm_panda")
    parent_mock.attach_mock(mock_disarm_panda, "mock_disarm_panda")
    parent_mock.attach_mock(mock_sleep, "mock_sleep")
    parent_mock.attach_mock(mock_reset_panda, "mock_reset_panda")

    RE(
        trigger_panda(
            panda=mock_panda,
            diffractometer=eh2_diffractometer,
            phi_start=5,
            phi_end=10,
            phi_steps=25,
            exposure_time=10,
        )
    )
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_has_calls([call(10, wait=True), call(5, wait=True)])

    expected_calls = [
        call.mock_setup_diffractometer(eh2_diffractometer, 5, 25, 10),
        call.mock_setup_diffractometer().__iter__(),
        call.mock_setup_panda_for_rotation(mock_panda, 5, 10, 25, 10),
        call.mock_setup_panda_for_rotation().__iter__(),
        call.mock_arm_panda(mock_panda),
        call.mock_arm_panda().__iter__(),
        call.mock_sleep(2.0),
        call.mock_sleep().__iter__(),
        call.mock_disarm_panda(mock_panda),
        call.mock_disarm_panda().__iter__(),
        call.mock_reset_panda(mock_panda),
        call.mock_reset_panda().__iter__(),
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
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(
        1, wait=True
    )
    mock_disarm_zebra.assert_called_once_with(eh2_zebra)


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_panda")
async def test_abort_panda(
    mock_disarm_panda: MagicMock,
    mock_panda: HDFPanda,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(abort_panda(eh2_diffractometer, mock_panda))
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(
        1, wait=True
    )
    mock_disarm_panda.assert_called_once_with(mock_panda)


async def test_move_diffractometer_back(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(move_diffractometer_back(eh2_diffractometer, 4))
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_called_once_with(4.0, wait=True)
