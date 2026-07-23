from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    _convert_beam_centre_to_pixels,
    calculate_beam_centre_from_lut,
    write_eiger_params,
)

lut_columns = [[85.0, 585.0], [69.66, 69.66], [81.09, 81.09]]


def test_convert_bc_to_pix(parameters):
    det_size_mm = parameters.detector_constants.DET_SIZE_CONSTANTS.det_dimension
    det_size_px = parameters.detector_constants.DET_SIZE_CONSTANTS.det_size_pixels
    beam_x, beam_y = _convert_beam_centre_to_pixels((20, 10), det_size_mm, det_size_px)

    assert beam_x == pytest.approx(266.67, 1e-2)
    assert beam_y == pytest.approx(133.33, 1e-2)


@patch("i19_bluesky.serial.device_setup_plans.eiger_metadata._read_converter_lut")
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
@patch("i19_bluesky.serial.device_setup_plans.eiger_metadata.bps.wait")
@patch(
    "i19_bluesky.serial.device_setup_plans.eiger_metadata.calculate_beam_centre_from_lut"
)
async def test_write_eiger_params(
    mock_bc_from_lut: MagicMock,
    mock_bps_wait: MagicMock,
    eh2_eiger: EigerDetector,
    parameters: SerialExperimentEh2,
    RE: RunEngine,
    wait: bool,
):
    mock_bc_from_lut.return_value = (100, 200)

    RE(
        write_eiger_params(
            parameters,
            17,
            0.6,
            eh2_eiger,
            wait=wait,
        )
    )
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
        mock_bps_wait.assert_called_once_with("eiger_metadata")
