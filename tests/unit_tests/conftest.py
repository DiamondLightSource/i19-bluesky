import asyncio
import time

import pytest
from blueapi.core import BlueskyContext
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.devices.zebra.zebra import Zebra
from ophyd_async.core import get_mock_put, set_mock_value


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
def context() -> BlueskyContext:
    return BlueskyContext()


@pytest.fixture
def eh2_zebra(RE: RunEngine) -> Zebra:
    zebra = i19_2.zebra(connect_immediately=True, mock=True)

    def mock_disarm(_, wait):
        set_mock_value(zebra.pc.arm.armed, 0)

    def mock_arm(_, wait):
        set_mock_value(zebra.pc.arm.armed, 1)

    get_mock_put(zebra.pc.arm.arm_set).side_effect = mock_arm
    get_mock_put(zebra.pc.arm.disarm_set).side_effect = mock_disarm
    return zebra
