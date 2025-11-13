import bluesky.plan_stubs as bps
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.diffractometer_setup import setup_diffractometer
from i19_bluesky.serial.panda_setup_plans import setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda

setup_diffractometer(
    phi_start=0, phi_steps=0, exposure_time=0, phi_value=0, phi_velocity=0
)


def trigger_panda(panda: HDFPanda, phi_value, phi_start, phi_end):
    yield from setup_panda_for_rotation(panda, 0, 0, 0, 0, 0)
    yield from arm_panda(panda)
    yield from bps.abs_set(phi_value, phi_end)
    yield from bps.wait()
    yield from bps.abs_set(phi_value, phi_start)
    yield from disarm_panda(panda)
