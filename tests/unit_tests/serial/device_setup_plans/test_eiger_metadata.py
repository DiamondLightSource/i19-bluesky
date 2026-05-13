import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    write_eiger_params,
)


@pytest.mark.parametrize(
    # "detector_distance_mm,two_theta_deg,phi_start,phi_increment,beam_center_x,
    # beam_center_y,energy",
    # [(100, 5, 4, 3, 2, 1, 6)],
    "detector_distance_mm,beam_center_x,beam_center_y,energy",
    [(100, 3, 2, 1)],
)
async def test_write_eiger_params(
    detector_distance_mm: float,
    # two_theta_deg: float,
    # phi_start: float,
    # phi_increment: float,
    beam_center_x: float,
    beam_center_y: float,
    energy: float,
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        write_eiger_params(
            detector_distance_mm,
            # two_theta_deg,
            # phi_start,
            # phi_increment,
            beam_center_x,
            beam_center_y,
            energy,
            eh2_eiger,
        )
    )
    assert (await eh2_eiger.drv.detector.detector_distance.get_value()) == 100
    assert (await eh2_eiger.drv.detector.beam_center_x.get_value()) == 3
    assert (await eh2_eiger.drv.detector.beam_center_y.get_value()) == 2
    assert (await eh2_eiger.drv.detector.photon_energy.get_value()) == 1
    assert (await eh2_eiger.drv.detector.omega_start.get_value()) == 0
    assert (await eh2_eiger.drv.detector.omega_increment.get_value()) == 0
    # assert (await eiger.drv.detector.wavelength.get_value()==12398.4/1 # type:ignore
    # assert (await eiger.drv.detector.two_theta.get_value()== 0  # type:ignore
    # assert (await eiger.drv.detector.phi_start.get_value()==0  # type:ignore
    # assert (await eiger.drv.detector.phi_increment.get_value()==0type:ignore
    # assert (await eiger.drv.detector.chi_start.get_value()==0  # type:ignore
    # assert (await eiger.drv.detector.chi_increment.get_value()==0  # type:ignore
    # assert (await eiger.drv.detector.kappa_start.get_value()==0  # type:ignore
    # assert (await eiger.drv.detector.kappa_increment.get_value()==0  # type:ignore
