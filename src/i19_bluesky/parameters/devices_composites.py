import pydantic
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinholeCollimatorControl,
)
from dodal.devices.motors import XYZPhiStage
from dodal.devices.zebra.zebra import Zebra
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class SerialCollectionEh2PandaComposite:
    diffractometer: FourCircleDiffractometer
    backlight: BacklightPosition
    pincol: PinholeCollimatorControl
    panda: HDFPanda
    eiger: EigerDetector
    serial_stages: XYZPhiStage


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class SerialCollectionEh2ZebraComposite:
    diffractometer: FourCircleDiffractometer
    backlight: BacklightPosition
    pincol: PinholeCollimatorControl
    zebra: Zebra
    eiger: EigerDetector
    serial_stages: XYZPhiStage
