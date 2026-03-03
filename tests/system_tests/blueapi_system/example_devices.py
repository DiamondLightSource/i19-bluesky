from enum import StrEnum

from bluesky.protocols import Movable
from dodal.common.beamlines.beamline_utils import (
    device_factory,
)
from dodal.devices.beamlines.i19.access_controlled.blueapi_device import (
    HutchState,
    OpticsBlueAPIDevice,
)
from dodal.devices.beamlines.i19.access_controlled.hutch_access import (
    HutchAccessControl,
)
from ophyd_async.core import AsyncStatus, StandardReadable
from ophyd_async.sim import SimMotor


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


@device_factory()
def optics_motors() -> FakeOpticsMotors:
    return FakeOpticsMotors(name="optics_motors")


@device_factory()
def access_device() -> HutchAccessControl:
    device = HutchAccessControl(prefix="MOCK-ACCESS-CONTROL:", name="access_control")
    return device


class AccessControlledOpticsMotors(OpticsBlueAPIDevice):
    def __init__(
        self,
        hutch: HutchState = HutchState.EH2,
        instrument_session: str = "cm12345-1",
        name: str = "",
    ) -> None:
        super().__init__(hutch, instrument_session, name)

    @AsyncStatus.wrap
    async def set(self, value: MotorPosition):
        request_params = {
            "name": "move_motors",
            "params": {
                "experiment_hutch": self._invoking_hutch,
                "access_device": "access_control",
                "position": value.value,
            },
            "instrument_session": "self.instrument",
        }
        await super().set(request_params)
