import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    write_eiger_params,
)


@pytest.mark.parametrize(
    "detector_distance_mm,two_theta_deg,phi_start,phi_increment,beam_center_x,beam_center_y,energy",
    [(100, 2, 2, 2, 2, 2, 2)],
)
async def test_write_eiger_params(
    detector_distance_mm: float,
    two_theta_deg: float,
    phi_start: float,
    phi_increment: float,
    beam_center_x: float,
    beam_center_y: float,
    energy: float,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        write_eiger_params(
            detector_distance_mm,
            two_theta_deg,
            phi_start,
            phi_increment,
            beam_center_x,
            beam_center_y,
            energy,
            eh2_eiger,
        )
    )
    assert (await eh2_eiger.drv.detector.detector_distance.get_value()) == 100
    assert (await eh2_eiger.drv.detector.beam_center_x.get_value()) == 2
    assert (await eh2_eiger.drv.detector.beam_center_y.get_value()) == 2
    assert (await eh2_eiger.drv.detector.photon_energy.get_value()) == 2
