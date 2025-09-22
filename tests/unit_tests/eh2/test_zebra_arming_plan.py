from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.zebra.zebra import ArmDemand, ArmingDevice

from i19_bluesky.eh2.zebra_arming_plan import (
    arm_zebra,
    disarm_zebra,
)


@patch("i19_bluesky.eh2.zebra_arming_plan.bps.abs_set")
async def test_arm_zebra_plan(
    mock_set: MagicMock, eh2_zebra: ArmingDevice, RE: RunEngine
):
    RE(arm_zebra(eh2_zebra))

    mock_set.assert_called_once_with(eh2_zebra, ArmDemand.ARM, wait=True)


@patch("i19_bluesky.eh2.zebra_disarming_plan.bps.abs_set")
async def test_disarm_zebra_plan(
    mock_set: MagicMock, eh2_zebra: ArmingDevice, RE: RunEngine
):
    RE(disarm_zebra(eh2_zebra))

    mock_set.assert_called_once_with(eh2_zebra, ArmDemand.DISARM, wait=True)


@pytest.mark.parametrize(
    "arm_set, specific_plan",
    [(ArmDemand.ARM, arm_zebra), (ArmDemand.DISARM, disarm_zebra)],
)
async def test_zebra_arming_plan(
    eh2_zebra: ArmingDevice, RE: RunEngine, arm_set, specific_plan
):
    RE(specific_plan(eh2_zebra))
    await eh2_zebra.set(arm_set)
    assert await eh2_zebra.arm_set.get_value() == arm_set
