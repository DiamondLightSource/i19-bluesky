from bluesky.run_engine import RunEngine
from dodal.devices.zebra.zebra import ArmDemand, Zebra

from i19_bluesky.eh2.zebra_arming_plan import (
    arm_zebra,
    disarm_zebra,
)


async def test_zebra_arm(eh2_zebra: Zebra, RE: RunEngine):
    RE(arm_zebra(eh2_zebra))
    assert await eh2_zebra.pc.arm.armed.get_value() == ArmDemand.ARM.value
    assert await eh2_zebra.pc.arm.arm_set.get_value() == 1


async def test_zebra_disarm(eh2_zebra: Zebra, RE: RunEngine):
    RE(disarm_zebra(eh2_zebra))
    assert await eh2_zebra.pc.arm.armed.get_value() == ArmDemand.DISARM.value
    assert await eh2_zebra.pc.arm.disarm_set.get_value() == 1
