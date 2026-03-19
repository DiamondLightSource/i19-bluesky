from unittest.mock import MagicMock, call, patch

from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.core import get_mock_put
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.panda_serial_collection import (
    abort_panda,
    trigger_panda,
)


@patch("i19_bluesky.serial.panda_serial_collection.reset_panda")
@patch("i19_bluesky.serial.panda_serial_collection.bps.sleep")
@patch("i19_bluesky.serial.panda_serial_collection.disarm_panda")
@patch("i19_bluesky.serial.panda_serial_collection.arm_panda")
@patch("i19_bluesky.serial.panda_serial_collection.setup_panda_for_rotation")
@patch("i19_bluesky.serial.panda_serial_collection.setup_diffractometer")
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
            det_z=100,
            det_x=100,
            phi_start=5,
            phi_end=10,
            phi_steps=25,
            exposure_time=10,
            panda=mock_panda,
            diffractometer=eh2_diffractometer,
        )
    )
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_has_calls([call(10), call(5)])

    expected_calls = [
        call.mock_setup_diffractometer(eh2_diffractometer, 5, 25, 10),
        call.mock_setup_panda_for_rotation(mock_panda, 5, 10, 25, 10),
        call.mock_arm_panda(mock_panda),
        call.mock_sleep(2.0),
        call.mock_disarm_panda(mock_panda),
        call.mock_reset_panda(mock_panda),
    ]

    parent_mock.assert_has_calls(expected_calls, any_order=True)


@patch("i19_bluesky.serial.panda_serial_collection.disarm_panda")
async def test_abort_panda(
    mock_disarm_panda: MagicMock,
    mock_panda: HDFPanda,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(abort_panda(eh2_diffractometer, mock_panda))
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_panda.assert_called_once_with(mock_panda)
