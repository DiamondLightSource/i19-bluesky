import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.motors import XYZPhiStage
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_stage_x_and_z,
)


def trigger_serial_collection(
    scan_start: float,
    scan_end: float,
    wells_to_collect: dict[str, tuple],
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
) -> MsgGenerator:
    """Kick off a serial collection with forwards and backwards rotations alternating at
    each well.

    Args:
        scan_start (float): Rotation start in positive direction, in deg.
        scan_end (float): Rotation end in positive direction, in deg.
        wells_to_collect (dict): Input coordinates of the selected wells
            (Key=well (int), value=X,Y,Z coordinates (list of ints))
        eiger (EigerDetector): The eiger detector device
        serial_stages (XYZPhiStage): The serial sample stage device
    """
    LOGGER.info("Kickoff eiger")
    yield from bps.kickoff(eiger, wait=True)
    for i, (well_num, coords) in enumerate(wells_to_collect.items()):
        yield from move_stage_x_and_z(coords[0], coords[2], serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        if i % 2 == 0:  # even in list
            LOGGER.info(f"Rotate {scan_start} to {scan_end}")
            yield from bps.abs_set(
                serial_stages.phi,
                scan_end,
                wait=True,
            )
        else:  # odd idx in list
            LOGGER.info(f"Rotate {scan_end} to {scan_start}")
            yield from bps.abs_set(
                serial_stages.phi,
                scan_start,
                wait=True,
            )
    LOGGER.info("Run complete eiger")
    yield from bps.complete(eiger, wait=True)
