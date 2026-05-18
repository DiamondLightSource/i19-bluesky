import bluesky.plan_stubs as bps
from ophyd_async.fastcs.eiger import EigerDetector


def write_eiger_params(
    detector_distance_mm: float,
    # two_theta_deg: float,
    # phi_start: float,
    # phi_increment: float,
    beam_center_x: float,
    beam_center_y: float,
    energy: float,
    eiger: EigerDetector,
):
    yield from bps.abs_set(eiger.detector.photon_energy, energy)
    yield from bps.abs_set(eiger.detector.detector_distance, detector_distance_mm)
    yield from bps.abs_set(eiger.detector.beam_center_x, beam_center_x)
    yield from bps.abs_set(eiger.detector.beam_center_y, beam_center_y)
    yield from bps.abs_set(eiger.detector.omega_start, 0)
    yield from bps.abs_set(eiger.detector.omega_increment, 0)
    # yield from bps.abs_set(eiger.detector.wavelength, 12398.4/energy)# type:ignore
    # yield from bps.abs_set(eiger.detector.two_theta, two_theta_deg)  # type:ignore
    # yield from bps.abs_set(eiger.detector.phi_start, phi_start)  # type:ignore
    # yield from bps.abs_set(eiger.detector.phi_increment, phi_increment)type:ignore
    # yield from bps.abs_set(eiger.detector.chi_start, 0)  # type:ignore
    # yield from bps.abs_set(eiger.detector.chi_increment, 0)  # type:ignore
    # yield from bps.abs_set(eiger.detector.kappa_start, 0)  # type:ignore
    # yield from bps.abs_set(eiger.detector.kappa_increment, 0)  # type:ignore
