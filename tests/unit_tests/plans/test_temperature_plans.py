from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.cryostream import OxfordCryoStream

from i19_bluesky.plans.temperature_control_plans import run_temperature_ramp


@pytest.fixture
async def cryostream(RE: RunEngine) -> OxfordCryoStream:
    cryo = OxfordCryoStream("", name="mock-cryo")
    await cryo.connect(mock=True)
    return cryo


@patch("i19_bluesky.plans.temperature_control_plans.bps.trigger")
async def test_run_temperature_ramp(
    mock_trigger: MagicMock, cryostream: OxfordCryoStream, RE: RunEngine
):
    RE(run_temperature_ramp(300, 320, cryostream))

    assert await cryostream.ramp_rate.get_value() == 320
    assert await cryostream.ramp_temp.get_value() == 300
    mock_trigger.assert_called_once_with(cryostream.ramp)
