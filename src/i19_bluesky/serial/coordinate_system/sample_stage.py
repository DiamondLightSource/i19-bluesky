import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer


def read_current_sample_stage_xyz_position(
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator[tuple[float, float, float]]:
    """Read the current position of the x,y,z motors of the sample stage on the
    diffractometer and return the values as a tuple.

    Args:
        diffractometer (FourCircleDiffractometer, optional): The diffractometer device.

    Returns:
        MsgGenerator[tuple[float, float, float]]: The (x,y,z) positions of the sample
        stage.
    """
    x = yield from bps.rd(diffractometer.x)
    y = yield from bps.rd(diffractometer.y)
    z = yield from bps.rd(diffractometer.z)
    return (x, y, z)


def move_sample_stage_to_corners(
    corner_coord: tuple[float, float, float],
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator:
    """Move the x,y,z motors of the sample stage to the fiducial positions.

    Args:
        corner_coord (tuple[float, float, float]): Coordinates of the fiducial corner.
        diffractometer (FourCircleDiffractometer, optional): The diffractometer device.
    """
    yield from bps.mv(
        diffractometer.x,
        corner_coord[0],
        diffractometer.y,
        corner_coord[1],
        diffractometer.z,
        corner_coord[2],
    )
