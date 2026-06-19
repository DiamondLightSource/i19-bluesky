from daq_config_server.models.lookup_tables import DetectorXYLookupTable
from dodal.common.beamlines.beamline_utils import (
    get_config_client,
)

BEAM_XY_TABLE_PATH = (
    "/dls_sw/i19-2/software/daq_configuration/lookup/DetDistToBeamXYConverterE4M.txt"
)


def _read_eiger_lookup_table():
    config_client = get_config_client()
    return config_client.get_file_contents(
        BEAM_XY_TABLE_PATH,
        DetectorXYLookupTable,
        force_parser=DetectorXYLookupTable.from_contents,
    )


def find_beam_xy(index: int):
    return tuple(_read_eiger_lookup_table().columns[index])
