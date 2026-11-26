import asyncio
import time
from typing import TypeVar
from unittest.mock import MagicMock

import bluesky.plan_stubs as bps
import pytest
from blueapi.core import BlueskyContext, MsgGenerator
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.devices.beamlines.i19.access_controlled.blueapi_device import HutchState
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
    FocusingMirrorName,
)
from dodal.devices.zebra.zebra import Zebra
from ophyd_async.core import get_mock_put, set_mock_value

T = TypeVar("T")


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


def fake_generator(return_val: T = None) -> MsgGenerator[T]:
    yield from bps.null()
    return return_val


@pytest.fixture
def eh2_zebra(RE: RunEngine) -> Zebra:
    zebra = i19_2.zebra.build(connect_immediately=True, mock=True)

    def mock_disarm(_):
        set_mock_value(zebra.pc.arm.armed, 0)

    def mock_arm(_):
        set_mock_value(zebra.pc.arm.armed, 1)

    get_mock_put(zebra.pc.arm.arm_set).side_effect = mock_arm
    get_mock_put(zebra.pc.arm.disarm_set).side_effect = mock_disarm
    return zebra


@pytest.fixture
async def eh1_hfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    hfm_piezo = AccessControlledPiezoActuator(
        "",
        FocusingMirrorName.HFM,
        HutchState.EH1,
        "/path/to/config/",
        MagicMock(),
        "",
        "mock_hfm_piezo",
    )
    await hfm_piezo.connect(mock=True)
    hfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(hfm_piezo.readback, 5.236)
    return hfm_piezo


@pytest.fixture
async def eh1_vfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    vfm_piezo = AccessControlledPiezoActuator(
        "",
        FocusingMirrorName.VFM,
        HutchState.EH1,
        "/path/to/config/",
        MagicMock(),
        "",
        "mock_vfm_piezo",
    )
    await vfm_piezo.connect(mock=True)
    vfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(vfm_piezo.readback, 0.849)
    return vfm_piezo


@pytest.fixture
async def eh2_hfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    hfm_piezo = AccessControlledPiezoActuator(
        "",
        FocusingMirrorName.HFM,
        HutchState.EH2,
        "/path/to/config/",
        MagicMock(),
        "",
        "mock_hfm_piezo",
    )
    await hfm_piezo.connect(mock=True)
    hfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(hfm_piezo.readback, 3.041)
    return hfm_piezo


@pytest.fixture
async def eh2_vfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    vfm_piezo = AccessControlledPiezoActuator(
        "",
        FocusingMirrorName.VFM,
        HutchState.EH2,
        "/path/to/config/",
        MagicMock(),
        "",
        "mock_hfm_piezo",
    )
    await vfm_piezo.connect(mock=True)
    vfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(vfm_piezo.readback, 1.675)
    return vfm_piezo
