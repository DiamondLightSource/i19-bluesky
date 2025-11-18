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
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_diffractometer(5.0, 10, 2, eh2_diffractometer))
    set_mock_value(eh2_diffractometer.phi.user_readback, 5.0)
    assert await eh2_diffractometer.phi.user_readback.get_value() == 5
    assert await eh2_diffractometer.phi.velocity.get_value() == 5


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
    eh2_diffractometer: FourCircleDiffractometer,
    rotation_direction: RotationDirection,
    RE: RunEngine,
):
    RE(
        setup_zebra(
            eh2_zebra, 5.0, 10, 3, 4, 10, 20, eh2_diffractometer, rotation_direction
        )
    )
    mock_setup_diffractometer.assert_called_once_with(5, 10, 20, eh2_diffractometer)
    mock_setup_zebra_for_collection.assert_called_once_with(
        eh2_zebra,
        rotation_direction,
        4,
        3,
        4,
    )
    mock_setup_out_triggers.assert_called_once_with(eh2_zebra)
    mock_setup_zebra_for_triggering.assert_called_once_with(eh2_zebra)
    set_mock_value(eh2_diffractometer.phi.user_readback, 7)
    assert await eh2_diffractometer.phi.user_readback.get_value() == 7


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
    RE: RunEngine,
    mock_panda: HDFPanda,
    eh2_diffractometer: FourCircleDiffractometer,
):
    phi_start = 5
    phi_end = 10
    RE(trigger_panda(mock_panda, eh2_diffractometer, 4, phi_start, phi_end, 2, 30, 10))
    mock_setup_diffractometer.assert_called_once_with(5, 2, 30, eh2_diffractometer)
    mock_setup_panda_for_rotation.assert_called_once_with(
        mock_panda, 4, phi_start, phi_end, 2, 10
    )
    mock_arm_panda.assert_called_once_with(mock_panda)
    set_mock_value(eh2_diffractometer.phi.user_readback, phi_end)
    assert await eh2_diffractometer.phi.user_readback.get_value() == phi_end
    set_mock_value(eh2_diffractometer.phi.user_readback, phi_start)
    assert await eh2_diffractometer.phi.user_readback.get_value() == phi_start
    mock_disarm_panda.assert_called_once_with(mock_panda)
