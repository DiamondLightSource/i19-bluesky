"""System test for blueapi backed device used for access control on i19.

HOWTO:
- Step 1: Start blueapi server with no stompo configuration, which mirrors
   the optics blueapi running on i19
       blueapi -c no_stomp_config.yaml serve
- Step 2: Run system tests
       tox -e system-test
"""

import time
from pathlib import Path

import pytest
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig, RestConfig
from blueapi.service.model import DeviceResponse, PlanResponse
from pydantic import HttpUrl, TypeAdapter
from requests.exceptions import ConnectionError

from .blueapi_system.example_devices_and_plans import (
    AccessControlledOpticsMotors,
    # FakeOpticsMotors,
    # MotorPosition,  # , move_motors
)

CONFIG = ApplicationConfig(api=RestConfig(url=HttpUrl("http://localhost:12345")))


@pytest.fixture
def blueapi_client() -> BlueapiClient:
    return BlueapiClient.from_config(config=CONFIG)


@pytest.fixture(scope="module", autouse=True)
def wait_for_server():
    client = BlueapiClient.from_config(config=CONFIG)

    for _ in range(20):
        try:
            client.get_environment()
            return
        except ConnectionError:
            ...
        time.sleep(0.5)
    raise TimeoutError("No connection to blueapi server")


@pytest.fixture(autouse=True)
def clean_existing_tasks(blueapi_client: BlueapiClient):
    for task in blueapi_client.get_all_tasks().tasks:
        blueapi_client.clear_task(task.task_id)
    yield


@pytest.fixture
async def eh2_motors_with_blueapi() -> AccessControlledOpticsMotors:
    ac_motors = AccessControlledOpticsMotors(name="motors_with_blueapi")
    ac_motors.url = "https://localhost:12345"
    await ac_motors.connect()
    return ac_motors


# @pytest.mark.system_test
# async def test_move_motors_plan_does_not_run_when_check_access_fails(
#     eh2_motors_with_blueapi: AccessControlledOpticsMotors,
#     blueapi_client: BlueapiClient,
#     MOTOR: FakeOpticsMotors,
# ):
#     assert await MOTOR.motor1.user_readback.get_value() == 0.0
#     assert await MOTOR.motor2.user_readback.get_value() == 0.0

#     await eh2_motors_with_blueapi.set(MotorPosition.IN)

#     assert await MOTOR.motor1.user_readback.get_value() == 0.0
#     assert await MOTOR.motor2.user_readback.get_value() == 0.0


_DATA_PATH = Path(__file__).parent / "blueapi_system"


@pytest.fixture
def expected_plans() -> PlanResponse:
    return TypeAdapter(PlanResponse).validate_json(
        (_DATA_PATH / "plans.json").read_text()
    )


@pytest.mark.system_test
def test_get_plans_by_name(blueapi_client: BlueapiClient, expected_plans: PlanResponse):
    for plan in expected_plans.plans:
        assert blueapi_client.get_plan(plan.name) == plan


@pytest.fixture
def expected_devices() -> DeviceResponse:
    return TypeAdapter(DeviceResponse).validate_json(
        (_DATA_PATH / "devices.json").read_text()
    )


def test_get_devices(blueapi_client: BlueapiClient, expected_devices: DeviceResponse):
    retrieved_devices = blueapi_client.get_devices()
    retrieved_devices.devices.sort(key=lambda x: x.name)
    expected_devices.devices.sort(key=lambda x: x.name)

    assert retrieved_devices == expected_devices


# @pytest.mark.system_test
# def test_motors_move_when_hutch_check_passes():
#     pass
