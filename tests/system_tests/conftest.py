import asyncio
import time

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.i19.blueapi_device import HutchState
from ophyd_async.testing import set_mock_value

from .blueapi_system.example_devices import (
    AccessControlledOpticsMotors,
    FakeOpticsMotors,
    optics_motors,
)


@pytest.fixture
async def RE():
    RE = RunEngine({}, call_returns_result=True)
    # make sure the event loop is thoroughly up and running before we try to create
    # any ophyd_async devices which might need it
    timeout = time.monotonic() + 1
    while not RE.loop.is_running():
        await asyncio.sleep(0)
        if time.monotonic() > timeout:
            raise TimeoutError("This really shouldn't happen but just in case...")
    yield RE


@pytest.fixture
async def sim_motors(RE) -> FakeOpticsMotors:
    sim_motors = optics_motors(connect_immediately=True)
    set_mock_value(sim_motors.motor1.user_setpoint, 0.0)
    set_mock_value(sim_motors.motor2.user_setpoint, 0.0)
    return sim_motors


@pytest.fixture
async def eh2_motors_with_blueapi(RE) -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(name="motors_with_blueapi")
    ac_motors.url = "http://localhost:12345"
    await ac_motors.connect()
    return ac_motors


@pytest.fixture
async def eh1_motors_with_blueapi(RE) -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(
        hutch=HutchState.EH1, name="motors_with_blueapi"
    )
    ac_motors.url = "http://localhost:12345"
    await ac_motors.connect()
    return ac_motors
