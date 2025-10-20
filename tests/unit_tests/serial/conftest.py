from unittest.mock import MagicMock

import pytest
from ophyd_async.fastcs.panda import HDFPanda


@pytest.fixture
async def panda():
    panda = HDFPanda(prefix="Test", path_provider=MagicMock())
    await panda.connect(mock=True)
    return panda
