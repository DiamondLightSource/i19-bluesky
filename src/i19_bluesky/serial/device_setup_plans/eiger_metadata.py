import bluesky.plan_stubs as bps
from ophyd_async.fastcs.eiger import EigerDetector


def write_eiger_params(
    detector_distance_mm: float,
    two_theta_deg: float,
    phi_start: float,
    phi_increment: float,
    beam_center: tuple,
    energy: float,
    wavelength: float,
    eiger: EigerDetector,
    wait: bool,
    group: str = "eiger_metadata",
):
    yield from bps.abs_set(eiger.detector.photon_energy, energy, group=group)
    yield from bps.abs_set(
        eiger.detector.detector_distance, detector_distance_mm, group=group
    )
    yield from bps.abs_set(eiger.detector.beam_center_x, beam_center[0], group=group)
    yield from bps.abs_set(eiger.detector.beam_center_y, beam_center[1], group=group)
    yield from bps.abs_set(eiger.detector.omega_start, 0, group=group)
    yield from bps.abs_set(eiger.detector.omega_increment, 0, group=group)
    yield from bps.abs_set(
        eiger.detector.wavelength,  # type:ignore
        wavelength,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.two_theta,  # type:ignore
        two_theta_deg,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.phi_start,  # type:ignore
        phi_start,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.phi_increment,  # type:ignore
        phi_increment,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.chi_start,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.chi_increment,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.kappa_start,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.kappa_increment,  # type:ignore
        0,
        group=group,
    )
    if wait:
        bps.wait(group)
