import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer


def read_current_sample_stage_xyz_position(
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator[tuple[float, float, float]]:
    x = yield from bps.rd(diffractometer.x)
    y = yield from bps.rd(diffractometer.y)
    z = yield from bps.rd(diffractometer.z)
    return (x, y, z)


def move_sample_stage_to_corners(
    corner_coord: tuple[float, float, float],
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator:
    yield from bps.mv(
        diffractometer.x,
        corner_coord[0],
        diffractometer.y,
        corner_coord[1],
        diffractometer.z,
        corner_coord[2],
    )
