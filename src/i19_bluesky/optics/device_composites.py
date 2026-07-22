from dodal.devices.beamlines.i19.mirror_stripes import MirrorStripes
from dodal.devices.common_dcm import DoubleCrystalMonochromatorWithDSpacing
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.undulator import UndulatorInKeV
from pydantic import dataclasses


@dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class SetEnergyComposite:
    "Devices to be set when changing the energy"

    dcm: DoubleCrystalMonochromatorWithDSpacing
    undulator: UndulatorInKeV
    hfm: FocusingMirrorWithPiezo
    vfm: FocusingMirrorWithPiezo
    mirror_stripes: MirrorStripes
