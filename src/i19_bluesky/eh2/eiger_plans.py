import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.components import PandaRotationParams
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_sample_stage_back,
    move_stage_x_and_z,
    setup_sample_stage,
)
from i19_bluesky.serial.panda_setup_plans.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)
from i19_bluesky.serial.panda_setup_plans.panda_stubs import disarm_panda


# TODO: change away from serialexperiment? or hard code in some values.
def end_simple_run(
    parameters: SerialExperimentEh2,
    serial_stages: XYZPhiStage,
    panda: HDFPanda,
    eiger: EigerDetector,
):
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(eiger.drv.detector.disarm)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)
    yield from move_sample_stage_back(serial_stages, parameters.rot_axis_start)


def abort_simple_run(
    diffractometer: FourCircleDiffractometer,
    panda: HDFPanda,
    eiger: EigerDetector,
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(eiger.drv.detector.disarm)
    yield from disarm_panda(panda)


def setup_small_plan(
    PandaParams: PandaRotationParams,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
):
    yield from bps.stage(eiger)
    setup_panda_for_rotation(PandaParams, panda)
    yield from setup_sample_stage(
        PandaParams,
        serial_stages,
    )
    yield from bps.prepare(eiger, wait=True)


def loop_plan(
    parameters: SerialExperimentEh2,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
    well_num: int,
):
    yield from bps.kickoff(eiger, wait=True)
    if well_num % 2 == 0:
        LOGGER.info(
            f"Rotate {parameters.rot_axis_start} to\
                {parameters.panda_rotation_params.scan_end_deg}"
        )
        yield from bps.abs_set(
            diffractometer.phi,
            parameters.panda_rotation_params.scan_end_deg,
            wait=True,
        )
    else:
        LOGGER.info(
            f"Rotate {parameters.panda_rotation_params.scan_end_deg} to\
                    {parameters.rot_axis_start}"
        )
        yield from bps.abs_set(diffractometer.phi, parameters.rot_axis_start, wait=True)
    bps.complete(eiger, wait=True)


def run_eiger(
    parameters: SerialExperimentEh2,
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
):
    for well_num, coords in parameters.well_position.items():
        yield from move_stage_x_and_z(coords[0], coords[2], serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        loop_plan(parameters, eiger, diffractometer, well_num)


def run_small_plan(
    parameters: SerialExperimentEh2,
    PandaParams: PandaRotationParams,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
):
    setup_small_plan(PandaParams, eiger, panda, serial_stages)
    run_eiger(parameters, eiger, serial_stages, diffractometer)


def run_serial_small_plan(
    parameters: SerialExperimentEh2,
    PandaParams: PandaRotationParams,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
):
    yield from bpp.contingency_wrapper(
        run_small_plan(
            parameters, PandaParams, eiger, panda, serial_stages, diffractometer
        ),
        except_plan=abort_simple_run(diffractometer, panda, eiger),
        final_plan=end_simple_run(parameters, serial_stages, panda, eiger),
        auto_raise=False,
    )
