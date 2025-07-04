import pytest
from dodal.devices.i19.blueapi_device import HutchState
from ophyd_async.testing import set_mock_value

from .blueapi_system.example_devices import (
    AccessControlledOpticsMotors,
    FakeOpticsMotors,
    optics_motors,
)


@pytest.fixture
async def sim_motors() -> FakeOpticsMotors:
    sim_motors = optics_motors(connect_immediately=True)
    set_mock_value(sim_motors.motor1.user_setpoint, 0.0)
    set_mock_value(sim_motors.motor2.user_setpoint, 0.0)
    return sim_motors


@pytest.fixture
async def eh2_motors_with_blueapi() -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(name="motors_with_blueapi")
    ac_motors.url = "https://localhost:12345"
    await ac_motors.connect()
    return ac_motors


@pytest.fixture
async def eh1_motors_with_blueapi() -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(
        hutch=HutchState.EH1, name="motors_with_blueapi"
    )
    ac_motors.url = "https://localhost:12345"
    await ac_motors.connect()
    return ac_motors
