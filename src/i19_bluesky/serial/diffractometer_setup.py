import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator


def setup_diffractometer(
    phi_start, phi_steps, exposure_time, phi_value, phi_velocity
) -> MsgGenerator:
    """Setup phi on the diffractometer"""
    yield from bps.abs_set(phi_value, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(phi_velocity, velocity)
