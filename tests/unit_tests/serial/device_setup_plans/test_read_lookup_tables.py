from unittest.mock import patch

from daq_config_server.models.lookup_tables import DetectorXYLookupTable

from i19_bluesky.serial.device_setup_plans.read_lookup_tables import (
    _read_eiger_lookup_table,
    find_beam_xy,
)

CONTENT = """
#Table giving centre position of beam X and Y as a function of detector distance
#
# Columns: detector distance, x-centre, y-centre
Units mm mm mm
85  74.25 106.67
585 74.25 106.67
"""


@patch(
    "i19_bluesky.serial.device_setup_plans.read_lookup_tables.get_config_client",
)
# check if one value (chosen arbitrarily) does provide the correct corresponding value
def test_read_eiger_lookup_table(mock_client):
    returned_file = DetectorXYLookupTable.from_contents(CONTENT)
    mock_client.return_value.get_file_contents.return_value = returned_file

    assert (
        _read_eiger_lookup_table().get_value(
            search_column_name="beam_centre_x_mm",
            value=74.25,
            target_column_name="beam_centre_y_mm",
        )
        == 106.67
    )


@patch("i19_bluesky.serial.device_setup_plans.read_lookup_tables.get_config_client")
def test_find_beam_xy(mock_client):
    returned_file = DetectorXYLookupTable.from_contents(CONTENT)
    mock_client.return_value.get_file_contents.return_value = returned_file
    assert find_beam_xy(0) == (85.0, 585.0)
