from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.fastcs.panda import HDFPanda
from ophyd_async.testing import set_mock_value

from i19_bluesky.serial.example_trigger_plan_zebra_vs_panda import (
    setup_diffractometer,
    setup_zebra,
    trigger_panda,
)


async def test_setup_diffractometer(
    serial_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_diffractometer(5.0, 10, 2, serial_diffractometer))
    set_mock_value(serial_diffractometer.phi.user_readback, 5.0)
    assert await serial_diffractometer.phi.user_readback.get_value() == 5
    assert await serial_diffractometer.phi.velocity.get_value() == 5


@patch(
    "i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_zebra_for_triggering"
)
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_out_triggers")
@patch(
    "i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_zebra_for_collection"
)
@patch("i19_bluesky.serial.example_trigger_plan_zebra_vs_panda.setup_diffractometer")
@pytest.mark.parametrize(
    "rotation_direction", [RotationDirection.POSITIVE, RotationDirection.NEGATIVE]
)
async def test_setup_zebra(
    mock_setup_diffractometer: MagicMock,
    mock_setup_zebra_for_collection: MagicMock,
    mock_setup_out_triggers: MagicMock,
    mock_setup_zebra_for_triggering: MagicMock,
    eh2_zebra: Zebra,
    serial_diffractometer: FourCircleDiffractometer,
    rotation_direction: RotationDirection,
    RE: RunEngine,
):
    RE(setup_zebra(eh2_zebra, 0, serial_diffractometer, rotation_direction))
    mock_setup_diffractometer.assert_called_once_with(0, 0, 0, serial_diffractometer)
    mock_setup_zebra_for_collection.assert_called_once_with(
        eh2_zebra,
        rotation_direction,
        0,
        0,
        0,
    )
    mock_setup_out_triggers.assert_called_once_with(eh2_zebra)
    mock_setup_zebra_for_triggering.assert_called_once_with(eh2_zebra)
    set_mock_value(serial_diffractometer.phi.user_readback, 7)
    assert await serial_diffractometer.phi.user_readback.get_value() == 7


async def test_trigger_panda(
    mock_panda: HDFPanda,
    serial_diffractometer: FourCircleDiffractometer,
    mock_setup_diffractometer: MagicMock,
    mock_setup_panda_for_rotation: MagicMock,
    mock_arm_panda: MagicMock,
    mock_disarm_panda: MagicMock,
    phi_start,
    phi_end,
    RE: RunEngine,
):
    RE(trigger_panda(mock_panda, serial_diffractometer, phi_start=7, phi_end=6))
    mock_setup_diffractometer.assert_called_once_with(0, 0, 0, serial_diffractometer)
    mock_setup_panda_for_rotation.assert_called_once_with(0, 0, 0, mock_panda)
    mock_arm_panda.assert_called_once_with(mock_panda)
    set_mock_value(serial_diffractometer.phi.user_readback, phi_end)
    assert await serial_diffractometer.phi.user_readback.get_value() == 6
    # test bps sleep
    set_mock_value(serial_diffractometer.phi.user_readback, phi_start)
    assert await serial_diffractometer.phi.user_readback.get_value() == 7
    mock_disarm_panda.assert_called_once_with(mock_panda)
