import asyncio
import time

import pytest
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig, RestConfig
from bluesky.run_engine import RunEngine
from dodal.devices.i19.blueapi_device import HutchState
from pydantic import HttpUrl
from requests.exceptions import ConnectionError

from .blueapi_system.example_devices import (
    AccessControlledOpticsMotors,
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
