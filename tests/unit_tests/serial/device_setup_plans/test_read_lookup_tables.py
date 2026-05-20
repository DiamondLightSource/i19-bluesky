from unittest.mock import patch

from daq_config_server.models.lookup_tables import DetectorXYLookupTable

from i19_bluesky.serial.device_setup_plans.read_lookup_tables import (
    read_eiger_lookup_table,
)


@patch(
    "i19_bluesky.serial.device_setup_plans.read_lookup_tables.config_client",
)
# check if one value (chosen arbitrarily) does provide the correct corresponding value
def test_read_eiger_lookup_table(mock_client):
    content = """
#Table giving centre position of beam X and Y as a function of detector distance
#
# Columns: detector distance, x-centre, y-centre
Units mm mm mm
85  74.25 106.67
585 74.25 106.67
"""
    returned_file = DetectorXYLookupTable.from_contents(content)
    mock_client.return_value.get_file_contents.return_value = returned_file

    assert (
        read_eiger_lookup_table().get_value(
            search_column_name="beam_centre_x_mm",
            value=74.25,
            target_column_name="beam_centre_y_mm",
        )
        == 106.67
    )
