# Entrypoint plan
# Inject, a type, and a msg generator
# should be exposed to blueAPI by having it in__init__
# must create new file "run serial with panda"
# has contingency wrapper like this that calls 2 plans
# like doing try except finally
# any raise error / abort will go into except plan
# then will run final plan regardless (to reset)
# all in bluesky docs
# also in this you have main_collection_plan which will replace the contingency wrapper
# will call setup beamline then trigger_panda
# then: go to the UI and use blueAPI client (will hopefully be updated today)
# this will then run this test run serial with panda test
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.example_trigger_plan_zebra_vs_panda import (
    abort_panda,
    move_diffractometer_back,
    trigger_panda,
)
from i19_bluesky.serial.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def main_entry_point(
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    eh2_backlight: BacklightPosition = inject("backlight"),
    pincol: PinholeCollimatorControl = inject("pincol"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment. \
    Has contingencies to abort if any stage produces errors, before moving the \
    diffractometer to its starting position. Designed to be called with BlueAPI
    Args:
        detector_z (float): Distance to move in Z axis
        two_theta (float) Distance to move in Two-Theta axis
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
        aperture : PinColRequest object (StrEnum)
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        backlight : Backlight controller object
        pinhole_collimator : Pinhole Collimator control object
        panda (HDFPanda): The fastcs PandA ophyd device.
    """

    yield from bpp.contingency_wrapper(
        setup_beamline_before_collection(
            detector_z,
            detector_two_theta,
            eh2_backlight,
            eh2_diffractometer,
            pincol,
            eh2_aperture,
        ),
        except_plan=lambda: (yield from abort_panda(eh2_diffractometer, panda)),
    )
    yield from bpp.contingency_wrapper(
        trigger_panda(
            panda,
            eh2_diffractometer,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
        ),
        except_plan=lambda: (yield from abort_panda(eh2_diffractometer, panda)),
        final_plan=lambda: (
            yield from move_diffractometer_back(eh2_diffractometer, phi_start)
        ),
        auto_raise=False,
    )
