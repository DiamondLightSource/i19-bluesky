import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.diffractometer import FourCircleDiffractometer


def setup_diffractometer(
    phi_start: float,
    phi_steps: int,
    exposure_time: int,
    phi_velocity: float,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Setup phi on the diffractometer"""
    yield from bps.abs_set(diffractometer.phi, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(phi_velocity, velocity)
