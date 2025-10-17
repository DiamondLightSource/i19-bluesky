import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.fastcs.panda import HDFPanda


@pytest.fixture
async def serial_panda(RE: RunEngine) -> HDFPanda:
    panda = HDFPanda("", name="mock_panda")
    await panda.connect(mock=True)
    return panda
