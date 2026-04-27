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


def move_sample_stage(
    coord: tuple[float, float, float],
    sample_stage: XYZPhiStage = inject("serial_stages"),
) -> MsgGenerator:
    """Move the x,y,z motors of the sample stage to the fiducial positions.

    Args:
        coord (tuple[float, float, float]): Coordinates to move to.
        sample_stage (XYZPhiStage, optional): The serial sample stage device.
    """
    yield from bps.mv(
        sample_stage.x,
        coord[0],
        sample_stage.y,
        coord[1],
        sample_stage.z,
        coord[2],
    )


def run_coordinate_system_test(
    coord_list: list[tuple], sample_stage: XYZPhiStage = inject("serial_stages")
) -> MsgGenerator:
    """Utility function to run a test from the UI to check that the coordinates for the
    chip are all correct"""
    for coords in coord_list:
        yield from move_sample_stage(coords, sample_stage)
