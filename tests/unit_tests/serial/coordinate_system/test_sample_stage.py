from unittest.mock import MagicMock, patch

from bluesky import RunEngine
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import set_mock_value

from i19_bluesky.serial.coordinate_system.sample_stage import (
    move_sample_stage,
    read_current_sample_stage_xyz_position,
    run_coordinate_system_test,
)


def test_read_current_xyz_position(serial_stages: XYZPhiStage, RE: RunEngine):
    set_mock_value(serial_stages.x.user_readback, 2.4)
    set_mock_value(serial_stages.y.user_readback, 0.0)
    set_mock_value(serial_stages.z.user_readback, 0.5)

    res = RE(read_current_sample_stage_xyz_position(serial_stages)).plan_result  # type: ignore

    assert res == (2.4, 0.0, 0.5)


async def test_move_sample_to_position(serial_stages: XYZPhiStage, RE: RunEngine):
    RE(move_sample_stage((0.1, 1.2, 0.8), serial_stages))

    assert await serial_stages.x.user_readback.get_value() == 0.1
    assert await serial_stages.y.user_readback.get_value() == 1.2
    assert await serial_stages.z.user_readback.get_value() == 0.8


@patch("i19_bluesky.serial.coordinate_system.sample_stage.move_sample_stage")
def test_run_coordinate_system_test(
    mock_move_plan: MagicMock, serial_stages: XYZPhiStage, RE: RunEngine
):
    coordinates = [(0, 0, 0), (1, 2, 3), (4, 5, 6)]
    RE(run_coordinate_system_test(coordinates, serial_stages))

    assert mock_move_plan.call_count == len(coordinates)
