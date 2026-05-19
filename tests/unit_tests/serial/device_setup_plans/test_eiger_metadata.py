from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    write_eiger_params,
)


async def test_write_eiger_params(
    eh2_eiger: EigerDetector,
    RE: RunEngine,
    detector_distance_mm: float = 100,
    two_theta_deg: float = 0,
    phi_start: float = 0,
    phi_increment: float = 1,
    beam_center: tuple = (3, 2),
    wavelength: float = 100,
    energy: float = 10,
):
    RE(
        write_eiger_params(
            detector_distance_mm,
            two_theta_deg,
            phi_start,
            phi_increment,
            beam_center,
            energy,
            wavelength,
            eh2_eiger,
            wait=False,
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
