from pathlib import Path

from dodal.devices.detector.det_dim_constants import EIGER2_X_4M_SIZE
from pydantic.dataclasses import dataclass

EH2_DAQ_CONFIG_PATH = Path("/dls_sw/i19-2/software/daq_configuration")
EH2_BEAMLINE_PARAMS_PATH = EH2_DAQ_CONFIG_PATH / "domain/beamline.parameters"


@dataclass(frozen=True)
class EigerConstants:
    DET_DIST_LUT_PATH = EH2_DAQ_CONFIG_PATH / "lookup/DetDistToBeamXYConverterE4M.txt"
    DET_SIZE_CONSTANTS = EIGER2_X_4M_SIZE


@dataclass(frozen=True)
class DetectorConstants:
    EIGER = EigerConstants()
