import bluesky.plan_stubs as bps
from blueapi.core import MsgGenerator
from dodal.common import inject

from i19_bluesky.optics.check_access_control import check_access

from .example_devices import FakeOpticsMotors, MotorPosition

MOTOR: FakeOpticsMotors = inject("optics_motors")


@check_access
def move_motors(
    position: MotorPosition, motors: FakeOpticsMotors = MOTOR
) -> MsgGenerator:
    yield from bps.abs_set(motors, position, wait=True)
