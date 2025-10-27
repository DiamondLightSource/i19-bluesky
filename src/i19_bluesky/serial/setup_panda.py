import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.core import Device, DeviceVector, SignalRW
from ophyd_async.fastcs.core import fastcs_connector
from ophyd_async.fastcs.panda import PandaBitMux, PulseBlock, SeqBlock
from ophyd_async.fastcs.panda._table import SeqTable, SeqTrigger

from i19_bluesky.log import LOGGER

DEG_TO_ENC_COUNTS = 1000


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


class CustomPanda(Device):
    inenc: DeviceVector[InEnc]
    outenc: DeviceVector[OutEnc]
    seq: DeviceVector[SeqBlock]
    pulse: DeviceVector[PulseBlockWithEnable]

    def __init__(self, uri: str, name: str = "BL19-EA-PANDA-01"):
        super().__init__(name=name, connector=fastcs_connector(self, uri))


def arm_panda(panda: CustomPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to arm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ONE, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ONE, wait=True)  # type:ignore


def disarm_panda(panda: CustomPanda) -> MsgGenerator[None]:
    LOGGER.debug("Send command to disarm the PandA.")
    yield from bps.abs_set(panda.seq[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore
    yield from bps.abs_set(panda.pulse[1].enable, PandaBitMux.ZERO, wait=True)  # type: ignore


def generate_panda_seq_table(
    phi_start: float,
    phi_end: float,
    phi_steps: int,  # no. of images to take
    time_between_images: int,
) -> SeqTable:
    rows = SeqTable()  # type: ignore

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=int(phi_start * DEG_TO_ENC_COUNTS),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=int(phi_end * DEG_TO_ENC_COUNTS),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    return rows
