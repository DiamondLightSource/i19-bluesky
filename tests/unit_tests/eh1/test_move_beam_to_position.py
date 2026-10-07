from unittest.mock import MagicMock, patch

import pytest
from bluesky import RunEngine
from dodal.devices.oav.beam_centre.centroid_from_epics import CentroidFromEpics
from ophyd_async.core import set_mock_value

from i19_bluesky.eh1.move_beam_to_position import (
    _calculate_nudge_from_lut,
    _get_lut_path_and_column_from_name,
    _read_current_position,
)

TEST_HFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [-33.4, -8.35, 8.36, 33.8],
    [0.02, 0.04, 0.03, -0.09],
]
TEST_VFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [1.82, 0.45, -0.46, -1.86],
    [-37.67, -9.38, 9.33, 37.3],
]


async def test_read_current_position(beam_centre: CentroidFromEpics, RE: RunEngine):
    set_mock_value(beam_centre.beam_centre_x, 710)
    set_mock_value(beam_centre.beam_centre_y, 253)

    (beam_x, beam_y) = RE(_read_current_position(beam_centre)).plan_result

    assert await beam_centre.beam_centre_x.get_value() == beam_x
    assert await beam_centre.beam_centre_y.get_value() == beam_y


@pytest.mark.parametrize(
    "device_name, expected_idx, expected_filename",
    [
        ("hfm_piezo", 1, "hfm_nudge_to_position.txt"),
        ("vfm_piezo", 2, "vfm_nudge_to_position.txt"),
    ],
)
def test_get_lut_path_and_column_from_name(
    device_name: str, expected_idx: int, expected_filename: str
):
    idx, filepath = _get_lut_path_and_column_from_name(device_name)

    assert idx == expected_idx
    assert filepath.name == expected_filename


def test_get_lut_path_and_column_from_name_fails_for_unexpected_device():
    with pytest.raises(ValueError):
        _get_lut_path_and_column_from_name("beam_centre")


@pytest.mark.parametrize(
    "device_name, test_lut, distance, expected_nudge",
    [
        ("hfm_piezo", TEST_HFM_LUT_COLUMNS, 10, 0.012),
        ("vfm_piezo", TEST_VFM_LUT_COLUMNS, 20, 0.021),
    ],
)
@patch("i19_bluesky.eh1.move_beam_to_position._read_lut")
def test_calculate_nudge_from_lut(
    device_name: str,
    test_lut: list,
    distance: float,
    expected_nudge: float,
    mock_lut_columns: MagicMock,
):
    mock_lut_columns.return_value = test_lut
    nudge_size = _calculate_nudge_from_lut(distance, device_name)

    assert nudge_size == pytest.approxx(expected_nudge, 1e-3)
