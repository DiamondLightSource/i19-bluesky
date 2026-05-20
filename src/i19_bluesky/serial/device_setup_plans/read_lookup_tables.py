from daq_config_server.models.lookup_tables import DetectorXYLookupTable
from dodal.beamlines.i19_2 import config_client


def _read_eiger_lookup_table():
    return config_client().get_file_contents(
        "/dls_sw/i19-2/software/daq_configuration/lookup/"
        "DetDistToBeamXYConverterE4M.txt",
        DetectorXYLookupTable,
        force_parser=DetectorXYLookupTable.from_contents,
    )


def find_beam_xy(index: int):
    return tuple(_read_eiger_lookup_table().columns[index])
