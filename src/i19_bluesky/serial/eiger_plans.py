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


def end_simple_run(
    parameters: SerialExperimentEh2,
    serial_stages: XYZPhiStage,
    panda: HDFPanda,
    eiger: EigerDetector,
) -> MsgGenerator:
    LOGGER.info("Unstage eiger")
    yield from bps.unstage(eiger)
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
    yield from bps.unstage(eiger)
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(eiger.drv.detector.disarm)
    yield from disarm_panda(panda)


def setup_small_plan(
    params: SerialExperimentEh2,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
) -> MsgGenerator:
    yield from bps.stage(eiger)
    yield from setup_panda_for_rotation(params.panda_rotation_params, panda)
    yield from setup_sample_stage(
        params.panda_rotation_params,
        serial_stages,
    )
    yield from bps.prepare(eiger, wait=True)


def loop_plan(
    parameters: SerialExperimentEh2,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
    well_num: int,
) -> MsgGenerator:
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
    yield from bps.complete(eiger, wait=True)


def run_eiger(
    well_position: dict,
    parameters: SerialExperimentEh2,
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    for well_num, coords in well_position.items():
        yield from move_stage_x_and_z(coords[0], coords[2], serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        yield from loop_plan(parameters, eiger, diffractometer, well_num)


def run_small_plan(
    parameters: SerialExperimentEh2,
    well_position: dict,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    yield from setup_small_plan(parameters, eiger, panda, serial_stages)
    yield from run_eiger(
        well_position, parameters, eiger, serial_stages, diffractometer
    )


def run_serial_small_plan(
    parameters: SerialExperimentEh2,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    # not sure if this will work?
    parameters.rot_axis_increment = 0.1
    parameters.images_per_well = 1
    parameters.exposure_time_s = 0.2
    parameters.rot_axis_start = 5
    well_position = {1: [1, 2, 3], 2: [1, 2, 3]}
    yield from bpp.contingency_wrapper(
        run_small_plan(
            parameters, well_position, eiger, panda, serial_stages, diffractometer
        ),
        except_plan=abort_simple_run(diffractometer, panda, eiger),
        final_plan=end_simple_run(parameters, serial_stages, panda, eiger),
        auto_raise=False,
    )
