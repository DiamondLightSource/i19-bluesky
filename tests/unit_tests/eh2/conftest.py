import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.i19.shutter import AccessControlledShutter, HutchState


@pytest.fixture
async def eh2_shutter(RE: RunEngine) -> AccessControlledShutter:
    shutter = AccessControlledShutter("", HutchState.EH2, name="mock_shutter")
    await shutter.connect(mock=True)

    shutter.url = "http://test-blueapi.url"
    return shutter
