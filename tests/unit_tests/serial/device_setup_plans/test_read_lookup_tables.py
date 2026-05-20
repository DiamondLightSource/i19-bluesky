from daq_config_server.models.lookup_tables import DetectorXYLookupTable

from i19_bluesky.serial.device_setup_plans.read_lookup_tables import (
    read_eiger_lookup_table,
)


# check if one value (chosen arbitrarily) does provide the correct corresponding value
def test_read_eiger_lookup_table():
    assert isinstance(read_eiger_lookup_table(), DetectorXYLookupTable)
    assert (
        read_eiger_lookup_table().get_value(
            search_column_name="beam_centre_x_mm",
            value=74.25,
            target_column_name="beam_centre_y_mm",
        )
        == 106.67
    )
