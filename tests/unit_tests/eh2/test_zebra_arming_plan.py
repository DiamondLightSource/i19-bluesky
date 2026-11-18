from bluesky.run_engine import RunEngine
from dodal.devices.zebra.zebra import ArmDemand, Zebra

from i19_bluesky.eh2.zebra_arming_plan import (
    arm_zebra,
    disarm_zebra,
)


async def test_zebra_arm(zebra: Zebra, RE: RunEngine):
    RE(arm_zebra(zebra))
    assert await zebra.pc.arm.armed.get_value() == ArmDemand.ARM.value
    assert await zebra.pc.arm.arm_set.get_value() == 1


async def test_zebra_disarm(zebra: Zebra, RE: RunEngine):
    RE(disarm_zebra(zebra))
    assert await zebra.pc.arm.armed.get_value() == ArmDemand.DISARM.value
    assert await zebra.pc.arm.disarm_set.get_value() == 1
