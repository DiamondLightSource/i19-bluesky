from ophyd_async.core import Device, DeviceVector, SignalRW
from ophyd_async.fastcs.core import fastcs_connector
from ophyd_async.fastcs.panda import PandaBitMux, PulseBlock, SeqBlock


class InEnc(Device):
    val: SignalRW[PandaBitMux]


class OutEnc(Device):
    val: SignalRW[PandaBitMux]


class PulseBlockWithEnable(PulseBlock):
    enable: SignalRW[PandaBitMux]
    width: SignalRW[float]
    units: SignalRW[str]
    step: SignalRW[float]
    num_pulses: SignalRW[int]
    delay: SignalRW[float]


class panda(Device):
    inenc: DeviceVector[InEnc]
    outenc: DeviceVector[OutEnc]
    seq: DeviceVector[SeqBlock]
    pulse: DeviceVector[PulseBlockWithEnable]

    def __init__(self, uri: str, name: str = "BL19-EA-PANDA-01"):
        super().__init__(name=name, connector=fastcs_connector(self, uri))
