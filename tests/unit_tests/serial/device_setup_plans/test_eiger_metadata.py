from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    write_eiger_params,
)


@pytest.mark.parametrize("wait", [(False, True)])
@patch("i19_bluesky.serial.device_setup_plans.eiger_metadata.bps.wait")
async def test_write_eiger_params(
    mock_bps_wait: MagicMock,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
    wait: bool,
):

    RE(
        write_eiger_params(
            100,
            0,
            0,
            1,
            (3, 2),
            10,
            100,
            eh2_eiger,
            wait=wait,
        )
    )
    assert await eh2_eiger.detector.detector_distance.get_value() == 100
    assert await eh2_eiger.detector.beam_center_x.get_value() == 3
    assert await eh2_eiger.detector.beam_center_y.get_value() == 2
    assert await eh2_eiger.detector.photon_energy.get_value() == 10
    assert await eh2_eiger.detector.omega_start.get_value() == 0
    assert await eh2_eiger.detector.omega_increment.get_value() == 0
    assert await eh2_eiger.detector.wavelength.get_value() == 100  # type:ignore
    assert await eh2_eiger.detector.two_theta.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.phi_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.phi_increment.get_value() == 1  # type:ignore
    assert await eh2_eiger.detector.chi_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.chi_increment.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.kappa_start.get_value() == 0  # type:ignore
    assert await eh2_eiger.detector.kappa_increment.get_value() == 0  # type:ignore
    if wait:
        mock_bps_wait.assert_called_once_with("eiger_metadata")
