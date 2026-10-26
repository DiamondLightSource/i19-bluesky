from unittest.mock import MagicMock, call, patch

from bluesky import RunEngine
from dodal.devices.zebra.zebra import SoftInState, Zebra
from ophyd_async.core import get_mock_put

from i19_bluesky.serial.ui_plans.laser import run_laser_plan


@patch("i19_bluesky.serial.ui_plans.laser.bps.sleep")
async def test_laser_plan(mock_sleep: MagicMock, eh2_zebra: Zebra, RE: RunEngine):
    RE(run_laser_plan(2, eh2_zebra))

    soft_in_3 = get_mock_put(eh2_zebra.inputs.soft_in_3)

    assert await eh2_zebra.output.out_ttl_pvs[3].get_value() == 62

    mock_sleep.assert_called_once_with(2)

    soft_in_3.assert_has_calls([call(SoftInState.YES), call(SoftInState.NO)])
