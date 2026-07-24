from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from daq_config_server.models.lookup_tables import DetectorXYLookupTable
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.eiger_setup_plans import (
    _convert_beam_centre_to_pixels,
    _read_converter_lut,
    calculate_beam_centre_from_lut,
    set_eiger_params,
)

LUT_FILE = """
#Table giving centre position of beam X and Y as a function of detector distance
#
# Columns: detector distance, x-centre, y-centre
Units mm mm mm
85  69.66 81.09
585 69.66 81.09
"""

lut_columns = [[85.0, 585.0], [69.66, 69.66], [81.09, 81.09]]


def test_convert_bc_to_pix(parameters):
    det_size_mm = parameters.detector_constants.DET_SIZE_CONSTANTS.det_dimension
    det_size_px = parameters.detector_constants.DET_SIZE_CONSTANTS.det_size_pixels
    beam_x, beam_y = _convert_beam_centre_to_pixels((20, 10), det_size_mm, det_size_px)

    assert beam_x == pytest.approx(266.67, 1e-2)
    assert beam_y == pytest.approx(133.33, 1e-2)


@patch("i19_bluesky.serial.device_setup_plans.eiger_setup_plans.get_config_client")
def test_read_converter_lut(mock_config_client: MagicMock):
    file_contents = DetectorXYLookupTable.from_contents(LUT_FILE)
    mock_config_client.return_value.get_file_contents.return_value = file_contents
    cols = _read_converter_lut()

    assert cols == lut_columns


@patch("i19_bluesky.serial.device_setup_plans.eiger_setup_plans._read_converter_lut")
def test_calculate_beam_centre_from_lut(
    mock_read_lut: MagicMock, parameters: SerialExperimentEh2
):
    mock_read_lut.return_value = lut_columns

    (beam_centre_x, beam_centre_y) = calculate_beam_centre_from_lut(
        parameters.detector_distance_mm,
        parameters.detector_constants.DET_SIZE_CONSTANTS,
    )

    assert beam_centre_x == pytest.approx(928.80, 1e-2)
    assert beam_centre_y == pytest.approx(1081.2, 1e-2)


@pytest.mark.parametrize("wait", [(False, True)])
@patch("i19_bluesky.serial.device_setup_plans.eiger_setup_plans.bps.wait")
@patch(
    "i19_bluesky.serial.device_setup_plans.eiger_setup_plans.calculate_beam_centre_from_lut"
)
async def test_set_eiger_params(
    mock_bc_from_lut: MagicMock,
    mock_bps_wait: MagicMock,
    eh2_eiger: EigerDetector,
    parameters: SerialExperimentEh2,
    RE: RunEngine,
    wait: bool,
):
    mock_bc_from_lut.return_value = (100, 200)

    RE(
        set_eiger_params(
            parameters,
            17,
            0.6,
            eh2_eiger,
            wait=wait,
        )
    )
    assert await eh2_eiger.od.acquisition_id.get_value() == ""
    assert await eh2_eiger.od.file_path.get_value() == "/tmp/i19-2/cm12345-1/foo"
    assert await eh2_eiger.od.file_prefix.get_value() == "bar_01"
    assert await eh2_eiger.detector.detector_distance.get_value() == 320
    assert await eh2_eiger.detector.beam_center_x.get_value() == 100
    assert await eh2_eiger.detector.beam_center_y.get_value() == 200
    assert await eh2_eiger.detector.photon_energy.get_value() == 17
    assert await eh2_eiger.detector.omega_start.get_value() == 0
    assert await eh2_eiger.detector.omega_increment.get_value() == 0
    assert await eh2_eiger.detector.wavelength.get_value() == 0.6  # type:ignore
    assert await eh2_eiger.detector.two_theta.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.phi_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.phi_increment.get_value() == 0.1  # type:ignore
    assert await eh2_eiger.detector.chi_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.chi_increment.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.kappa_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.kappa_increment.get_value() == 0  # type:ignore
    if wait:
        mock_bps_wait.assert_called_once_with("eiger_setup")
