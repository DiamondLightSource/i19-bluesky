from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import Zebra
from ophyd_async.testing import set_mock_value

from i19_bluesky.serial.example_trigger_plan_zebra_vs_panda import (
    setup_diffractometer,
    setup_zebra_positive,
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
async def test_setup_zebra_positive(
    mock_setup_diffractometer: MagicMock,
    mock_setup_zebra_for_collection: MagicMock,
    mock_setup_out_triggers: MagicMock,
    mock_setup_zebra_for_triggering: MagicMock,
    eh2_zebra: Zebra,
    serial_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_zebra_positive(eh2_zebra, 0, serial_diffractometer))
    mock_setup_diffractometer.assert_called_once_with(0, 0, 0, serial_diffractometer)
    mock_setup_zebra_for_collection.assert_called_once_with(eh2_zebra)
    mock_setup_out_triggers.assert_called_once_with(eh2_zebra)
    mock_setup_zebra_for_triggering.assert_called_once_with(eh2_zebra)
    set_mock_value(serial_diffractometer.phi.user_readback, 0)
    assert await serial_diffractometer.phi.user_readback.get_value() == 0
