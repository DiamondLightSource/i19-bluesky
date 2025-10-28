import pytest
from dodal.beamlines.i19_2 import panda
from ophyd_async.fastcs.panda import HDFPanda


@pytest.fixture
async def mock_panda() -> HDFPanda:
    mocked_panda = panda()
    await mocked_panda.connect(mock=True)
    return mocked_panda
