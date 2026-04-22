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
from i19_bluesky.parameters.serial_parameters import PandaRotationParams
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
    rot_axis_start: float,
    serial_stages: XYZPhiStage,
    panda: HDFPanda,
    eiger: EigerDetector,
) -> MsgGenerator:
    LOGGER.info("Unstage eiger")
    yield from bps.unstage(eiger)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)
    yield from move_sample_stage_back(serial_stages, rot_axis_start)


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
    panda_rotation_params: PandaRotationParams,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
) -> MsgGenerator:
    yield from bps.stage(eiger)
    yield from setup_panda_for_rotation(panda_rotation_params, panda)
    yield from setup_sample_stage(
        panda_rotation_params,
        serial_stages,
    )
    yield from bps.prepare(eiger, wait=True)


def loop_plan_for_testing(
    panda_rotation_params: PandaRotationParams,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
    well_num: int,
) -> MsgGenerator:
    yield from bps.kickoff(eiger, wait=True)
    if well_num % 2 == 0:
        LOGGER.info(
            f"Rotate {panda_rotation_params.scan_start_deg} to\
                {panda_rotation_params.scan_end_deg}"
        )
        yield from bps.abs_set(
            diffractometer.phi,
            panda_rotation_params.scan_end_deg,
            wait=True,
        )
    else:
        LOGGER.info(
            f"Rotate {panda_rotation_params.scan_end_deg} to\
                    {panda_rotation_params.scan_start_deg}"
        )
        yield from bps.abs_set(
            diffractometer.phi, panda_rotation_params.scan_start_deg, wait=True
        )
    yield from bps.complete(eiger, wait=True)


def run_eiger(
    well_position: dict,
    panda_rotation_params: PandaRotationParams,
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
):
    # define loop plan here
    # Must make sure that we are actually prepared
    @bpp.run_decorator(md={"subplan_name": "loop_plan"})
    def loop_plan(
        panda_rotation_params: PandaRotationParams,
        eiger: EigerDetector,
        diffractometer: FourCircleDiffractometer,
        well_num: int,
    ) -> MsgGenerator:
        yield from bps.kickoff(eiger, wait=True)
        if well_num % 2 == 0:
            LOGGER.info(
                f"Rotate {panda_rotation_params.scan_start_deg} to\
                    {panda_rotation_params.scan_end_deg}"
            )
            yield from bps.abs_set(
                diffractometer.phi,
                panda_rotation_params.scan_end_deg,
                wait=True,
            )
        else:
            LOGGER.info(
                f"Rotate {panda_rotation_params.scan_end_deg} to\
                        {panda_rotation_params.scan_start_deg}"
            )
            yield from bps.abs_set(
                diffractometer.phi, panda_rotation_params.scan_start_deg, wait=True
            )
        yield from bps.complete(eiger, wait=True)

    for well_num, coords in well_position.items():
        yield from move_stage_x_and_z(coords[0], coords[2], serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        yield from loop_plan(panda_rotation_params, eiger, diffractometer, well_num)


def run_small_plan(
    panda_rotation_params: PandaRotationParams,
    well_position: dict,
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    yield from setup_small_plan(panda_rotation_params, eiger, panda, serial_stages)
    yield from run_eiger(
        well_position, panda_rotation_params, eiger, serial_stages, diffractometer
    )


def run_serial_small_plan(
    eiger: EigerDetector,
    panda: HDFPanda,
    serial_stages: XYZPhiStage,
    diffractometer: FourCircleDiffractometer,
    scan_start_deg: float = 0,
    scan_increment_deg: float = 0.1,
    scan_steps: int = 10,
    exposure_time_s: float = 0.2,
) -> MsgGenerator:
    # These are all the default values in the panda rotation params class (bar the scan
    # steps, which i've gone to 10, so we rotate 1 full degree), should provide somethi-
    # ng we can actually measure, and can be altered here
    panda_rotation_params = PandaRotationParams(
        scan_start_deg=scan_start_deg,
        scan_increment_deg=scan_increment_deg,
        scan_steps=scan_steps,
        exposure_time_s=exposure_time_s,
    )
    # These are just random numbers. Should move to position 1,3 (x,z) then 3,5 and go
    # from right to left then left to right before ending the run, rotating 1 degree
    well_position = {1: [1, 2, 3], 2: [3, 4, 5]}
    yield from bpp.contingency_wrapper(
        run_small_plan(
            panda_rotation_params,
            well_position,
            eiger,
            panda,
            serial_stages,
            diffractometer,
        ),
        except_plan=abort_simple_run(diffractometer, panda, eiger),
        final_plan=end_simple_run(
            panda_rotation_params.scan_start_deg, serial_stages, panda, eiger
        ),
        auto_raise=False,
    )
