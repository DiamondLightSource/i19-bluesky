"""System test for blueapi backed device used for access control on i19.

HOWTO:
- Step 1: Start softIOC simulating the hutch access device PVs
        python tests/system_tests/blueapi_system/fake_access_ioc.py
- Step 2: Start blueapi server with no stompo configuration, which mirrors
   the optics blueapi running on i19
       blueapi -c tests/system_tests/blueapi_system/config_optics_blueapi.yaml serve
- Step 3: Run system tests
       tox -e system-test
       (or pytest tests/system_tests)
"""

from pathlib import Path

import pytest
from blueapi.client.client import BlueapiClient
from blueapi.service.model import DeviceResponse, PlanResponse
from pydantic import TypeAdapter

from .blueapi_system.example_devices import (
    AccessControlledOpticsMotors,
    FakeOpticsMotors,
    MotorPosition,
)


@pytest.mark.system_test
async def test_blueapi_device_creates_and_completes_task_without_errors(
    eh2_motors_with_blueapi: AccessControlledOpticsMotors,
    blueapi_client: BlueapiClient,
):
    await eh2_motors_with_blueapi.set(MotorPosition.IN)

    task_list = blueapi_client.get_all_tasks()

    assert task_list.tasks[0].is_complete
    assert len(task_list.tasks[0].errors) == 0


@pytest.mark.system_test
async def test_move_motors_plan_does_not_run_when_check_access_fails(
    eh2_motors_with_blueapi: AccessControlledOpticsMotors,
    blueapi_client: BlueapiClient,
    sim_motors: FakeOpticsMotors,
):
    await eh2_motors_with_blueapi.set(MotorPosition.IN)

    assert await sim_motors.motor1.user_readback.get_value() == 0.0
    assert await sim_motors.motor2.user_readback.get_value() == 0.0


# @pytest.mark.system_test
# async def test_motors_move_when_hutch_check_passes(
#     eh1_motors_with_blueapi: AccessControlledOpticsMotors,
#     blueapi_client: BlueapiClient,
#     sim_motors: FakeOpticsMotors,
# ):
#     await eh1_motors_with_blueapi.set(MotorPosition.IN)

#     assert await sim_motors.motor1.user_readback.get_value() == 1.0
#     assert await sim_motors.motor2.user_readback.get_value() == 1.8


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


@pytest.mark.system_test
def test_get_devices(blueapi_client: BlueapiClient, expected_devices: DeviceResponse):
    retrieved_devices = blueapi_client.get_devices()
    retrieved_devices.devices.sort(key=lambda x: x.name)
    expected_devices.devices.sort(key=lambda x: x.name)

    assert retrieved_devices == expected_devices
