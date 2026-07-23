import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_sample_stage_back,
)
from i19_bluesky.serial.panda_plans.panda_setup_plans import reset_panda
from i19_bluesky.serial.panda_plans.panda_stubs import disarm_panda
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    trigger_panda_collection,
)
from i19_bluesky.serial.setup_beamline_plans.setup_beamline import (
    setup_eh2_serial_collection,
)


def main_collection_plan(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Run a small rotative serial crystallography collection using the PandA to trigger
    the detector."""
    yield from setup_eh2_serial_collection(parameters, devices)
    yield from trigger_panda_collection(parameters, devices)


def run_on_collection_end(
    rot_axis_start: float,
    panda: HDFPanda,
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
):
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(eiger.detector.disarm)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)
    yield from move_sample_stage_back(serial_stages, rot_axis_start)


def run_on_collection_abort(
    panda: HDFPanda,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(eiger.detector.disarm)
    yield from disarm_panda(panda)


@bpp.run_decorator()
def run_serial_with_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        main_collection_plan(parameters, devices),
        except_plan=lambda: (
            yield from run_on_collection_abort(
                devices.panda, devices.eiger, devices.diffractometer
            )
        ),
        final_plan=lambda: (
            yield from run_on_collection_end(
                parameters.rot_axis_start,
                devices.panda,
                devices.eiger,
                devices.serial_stages,
            )
        ),
        auto_raise=False,
    )
