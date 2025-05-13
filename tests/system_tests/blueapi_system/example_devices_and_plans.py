from enum import StrEnum

import bluesky.plan_stubs as bps
from blueapi.core import MsgGenerator
from bluesky.protocols import Movable
from dodal.common import inject
from dodal.devices.i19.blueapi_device import HutchState, OpticsBlueAPIDevice
from dodal.devices.i19.hutch_access import HutchAccessControl
from ophyd_async.core import AsyncStatus, StandardReadable
from ophyd_async.sim import SimMotor
from ophyd_async.testing import set_mock_value

from i19_bluesky.optics.check_access_control import check_access


class MotorPosition(StrEnum):
    IN = "IN"
    OUT = "OUT"


class FakeOpticsMotors(StandardReadable, Movable[MotorPosition]):
    def __init__(self, name: str = "") -> None:
        self.motor1 = SimMotor("m1")
        self.motor2 = SimMotor("m2")
        super().__init__(name)

    @AsyncStatus.wrap
    async def set(self, value: MotorPosition):
        if value == MotorPosition.IN:
            await self.motor1.set(1.0)
            await self.motor2.set(1.8)
        else:
            await self.motor1.set(0.0)
            await self.motor2.set(0.0)


async def optics_motors(name="optics_motors") -> FakeOpticsMotors:
    motors = FakeOpticsMotors(name=name)
    await motors.connect()
    await motors.set(MotorPosition.OUT)
    return motors


async def access_device(name="access_control") -> HutchAccessControl:
    device = HutchAccessControl(prefix="", name=name)
    await device.connect(mock=True)
    set_mock_value(device.active_hutch, "EH1")
    return device


class AccessControlledOpticsMotors(OpticsBlueAPIDevice):
    def __init__(self, name: str = "") -> None:
        self.hutch = HutchState.EH2
        super().__init__(name)

    @AsyncStatus.wrap
    async def set(self, value: MotorPosition):
        request_params = {
            "name": "move_motors",
            "params": {
                "experiment_hutch": self.hutch.value,
                "access_device": "access_control",
                "position": value.value,
            },
        }
        await super().set(request_params)


MOTOR: FakeOpticsMotors = inject("optics_motors")


@check_access
def move_motors(
    position: MotorPosition, motors: FakeOpticsMotors = MOTOR
) -> MsgGenerator:
    yield from bps.abs_set(motors, position, wait=True)
