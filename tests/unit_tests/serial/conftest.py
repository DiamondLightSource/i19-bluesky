import pytest

from i19_bluesky.serial.setup_panda import CustomPanda


@pytest.fixture
async def panda():
    mock_panda = CustomPanda("PANDA")
    await mock_panda.connect(mock=True)
    return mock_panda
