"""System test for blueapi backed device used for access control on i19.

HOWTO:
- Step 1: Start blueapi server with no stompo configuration, which mirrors
   the optics blueapi running on i19
       blueapi -c no_stomp_config.yaml serve
- Step 2: Run system tests
       tox -e system-test
"""

import time

import pytest
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig

from .blueapi_system.example_devices_and_plans import (
    MOTOR,
    AccessControlledOpticsMotors,  # , move_motors
    MotorPosition,
)


@pytest.fixture(scope="module", autouse=True)
def wait_for_server():
    client = BlueapiClient.from_config(config=ApplicationConfig())

    for _ in range(20):
        try:
            client.get_environment()
            return
        except ConnectionError:
            ...
        time.sleep(0.5)
    raise TimeoutError("No connection to blueapi server")


@pytest.fixture
def blueapi_client() -> BlueapiClient:
    return BlueapiClient.from_config(config=ApplicationConfig())


@pytest.fixture
async def eh2_motors_with_blueapi() -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(name="motors_with_blueapi")
    ac_motors.url = "https://testhost:12345"  # "https://localhost:8080"
    await ac_motors.connect()
    return ac_motors


@pytest.mark.system_test
async def test_move_motors_plan_does_not_run_when_check_access_fails(
    eh2_motors_with_blueapi: AccessControlledOpticsMotors,
    client: BlueapiClient,
    # MOTOR: FakeOpticsMotors,
):
    assert await MOTOR.motor1.user_readback.get_value() == 0.0
    assert await MOTOR.motor2.user_readback.get_value() == 0.0

    await eh2_motors_with_blueapi.set(MotorPosition.IN)

    assert await MOTOR.motor1.user_readback.get_value() == 0.0
    assert await MOTOR.motor2.user_readback.get_value() == 0.0


# @pytest.mark.system_test
# def test_motors_move_when_hutch_check_passes():
#     pass
