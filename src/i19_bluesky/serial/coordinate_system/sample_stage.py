import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.motors import XYZPhiStage


def read_current_sample_stage_xyz_position(
    sample_stage: XYZPhiStage = inject("serial_stages"),
) -> MsgGenerator[tuple[float, float, float]]:
    """Read the current position of the x,y,z motors of the sample stage on the
    diffractometer and return the values as a tuple.

    Args:
        sample_stage (XYZPhiStage, optional): The serial sample stage device.

    Returns:
        MsgGenerator[tuple[float, float, float]]: The (x,y,z) positions of the sample
        stage.
    """
    x = yield from bps.rd(sample_stage.x)
    y = yield from bps.rd(sample_stage.y)
    z = yield from bps.rd(sample_stage.z)
    return (x, y, z)


def move_sample_stage_to_corners(
    corner_coord: tuple[float, float, float],
    sample_stage: XYZPhiStage = inject("serial_stages"),
) -> MsgGenerator:
    """Move the x,y,z motors of the sample stage to the fiducial positions.

    Args:
        corner_coord (tuple[float, float, float]): Coordinates of the fiducial corner.
        sample_stage (XYZPhiStage, optional): The serial sample stage device.
    """
    yield from bps.mv(
        sample_stage.x,
        corner_coord[0],
        sample_stage.y,
        corner_coord[1],
        sample_stage.z,
        corner_coord[2],
    )
