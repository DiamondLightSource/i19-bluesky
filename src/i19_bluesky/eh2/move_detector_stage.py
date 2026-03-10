import bluesky.plan_stubs as bps
from dodal.devices.beamlines.i19.diffractometer import DetectorMotion


def move_stage(detector_stage: DetectorMotion, det_z: float, two_theta: float = 0.0):
    """Moves the Detector a distance of det_z and two_theta in the respective\
                directions. Order dependant on position of detector when \
                called.
        Args:
            detector_stage : DetectorMotion object
            det_z : Float
                Distance to move in Z axis
            two_theta : Float
                (default 0.0)
                Distance to move in Two-Theta axis
    """
    current_location = yield from bps.rd(detector_stage.det_z)
    if current_location >= det_z:
        # if the current value is higher than the requested one, first attempt to move
        # 2theta and then det_z
        yield from bps.mv(detector_stage.two_theta, two_theta)
        yield from bps.mv(detector_stage.det_z, det_z)
    else:
        # otherwise first move det_z and then 2theta
        yield from bps.mv(detector_stage.det_z, det_z)
        yield from bps.mv(detector_stage.two_theta, two_theta)


import bluesky.plan_stubs as bps
from dodal.devices.beamlines.i19.diffractometer import DetectorMotion


def move_detector_stage(
    detector_stage: DetectorMotion, det_z: float, two_theta: float = 0.0
):
    """Moves the Detector a distance of det_z and two_theta in the respective\
                directions. Order dependant on position of detector when \
                called.
        Args:
            detector_stage : DetectorMotion object
            det_z : Float
                Distance to move in Z axis
            two_theta : Float
                (default 0.0)
                Distance to move in Two-Theta axis
    """
    current_location = yield from bps.rd(detector_stage.det_z)
    if current_location >= det_z:
        # if the current value is higher than the requested one, first attempt to move
        # 2theta and then det_z
        yield from bps.mv(detector_stage.two_theta, two_theta)
        yield from bps.mv(detector_stage.det_z, det_z)
    else:
        # otherwise first move det_z and then 2theta
        yield from bps.mv(detector_stage.det_z, det_z)
        yield from bps.mv(detector_stage.two_theta, two_theta)
