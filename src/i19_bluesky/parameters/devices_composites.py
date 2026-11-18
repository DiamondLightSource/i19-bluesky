import pydantic
from dodal.devices.beamlines.i19.access_controlled.energy_device import (
    AccessControlledEnergyComposite,
)
from dodal.devices.beamlines.i19.access_controlled.shutter import (
    AccessControlledShutter,
)
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.beamstop import BeamStop
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinholeCollimatorControl,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class SerialCollectionEh2PandaComposite:
    diffractometer: FourCircleDiffractometer
    backlight: BacklightPosition
    beamstop: BeamStop
    pinhole_and_collimator: PinholeCollimatorControl
    panda: HDFPanda
    eiger: EigerDetector
    serial_stages: XYZPhiStage
    shutter: AccessControlledShutter
    energy_device: AccessControlledEnergyComposite
