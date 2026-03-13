from unittest.mock import MagicMock, call, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.core import get_mock_put
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.run_serial_with_panda import (
    abort_panda,
    move_diffractometer_back,
    setup_diffractometer,
    setup_then_trigger_panda,
    trigger_panda,
)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time",
    [(100, 30, 50, 60, 0.5, 0.2)],
)
@pytest.mark.parametrize(
    "eh2_aperture",
    [
        (PinColRequest.PCOL20),
        (PinColRequest.PCOL100),
    ],
)
async def test_main_entry_plan(
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    RE: RunEngine,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    mock_panda: HDFPanda,
):
    mock_main_entry_plan = MagicMock()
    RE(
        mock_main_entry_plan(
            detector_z,
            detector_two_theta,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            eh2_aperture,
            eh2_diffractometer,
            eh2_backlight,
            pincol,
            mock_panda,
        )
    )
    mock_main_entry_plan.assert_called_once()


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time",
    [(100, 30, 50, 60, 0.5, 0.2)],
)
@pytest.mark.parametrize(
    "eh2_aperture",
    [
        (PinColRequest.PCOL20),
        (PinColRequest.PCOL100),
    ],
)
@patch("i19_bluesky.serial.run_serial_with_panda.setup_beamline_before_collection")
async def test_setup_then_trigger_panda(
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    mock_panda: HDFPanda,
    RE: RunEngine,
    mock_setup_beamline_before_collection: MagicMock,
    mock_trigger_panda: MagicMock,
):
    parent_mock = MagicMock()
    parent_mock.attach_mock(
        mock_setup_beamline_before_collection, "mock_setup_beamline_before_collection"
    )
    parent_mock.attach_mock(mock_trigger_panda, "mock_trigger_panda")

    RE(
        setup_then_trigger_panda(
            detector_z,
            detector_two_theta,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            eh2_aperture,
            eh2_diffractometer,
            eh2_backlight,
            pincol,
            mock_panda,
        )
    )
    mock_setup_beamline_before_collection.assert_called_once()
    mock_trigger_panda.assert_called_once()
    assert eh2_diffractometer.det_stage.det_z == detector_z
    assert eh2_diffractometer.det_stage.two_theta == detector_two_theta


async def test_setup_diffractometer(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_diffractometer(eh2_diffractometer, 6.0, 10, 2))
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_called_once_with(6.0)

    mock_phi_velocity = get_mock_put(eh2_diffractometer.phi.velocity)
    mock_phi_velocity.assert_called_once_with(5.0)


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
    mock_phi.assert_has_calls([call(10), call(5)])

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


@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.disarm_panda")
async def test_abort_panda(
    mock_disarm_panda: MagicMock,
    mock_panda: HDFPanda,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(abort_panda(eh2_diffractometer, mock_panda))
    get_mock_put(eh2_diffractometer.phi.motor_stop).assert_called_once_with(1)
    mock_disarm_panda.assert_called_once_with(mock_panda)


async def test_move_diffractometer_back(
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(move_diffractometer_back(eh2_diffractometer, 4.0))
    mock_phi = get_mock_put(eh2_diffractometer.phi.user_setpoint)
    mock_phi.assert_called_once_with(4.0)
