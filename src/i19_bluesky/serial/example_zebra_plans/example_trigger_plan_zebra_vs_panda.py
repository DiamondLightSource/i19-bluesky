"""
Example trigger plan ZEBRA vs PandA.
"""

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2ZebraComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_sample_stage_back,
)
from i19_bluesky.serial.example_zebra_plans.zebra_collection_setup_plan import (
    setup_zebra_for_collection,
)
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    setup_sample_stage,
)

RAMP = 0.5


def trigger_zebra(
    gate_width: float,
    pulse_width: float,
    devices: SerialCollectionEh2ZebraComposite,
    parameters: SerialExperimentEh2,
) -> MsgGenerator:
    """Trigger zebra for collection in the forward and backward direction.
    Gate start is calculated as phi start - 0.5.
    Gate end is calculated as phi end + 0.5.

    Args:
        gate_width (float): Total distance from gate_start to gate_end, in degrees.
        pulse_width (float): Value comes from change in degrees of scan/velocity,\
        in seconds.
        devices (SerialCollectionEh2ZebraComposite) : SerialCollectionEh2ZebraComposite\
        object
        parameters: (SerialExperimentEh2) : SerialExperimentEh2 object
    """

    yield from setup_sample_stage(
        parameters.zebra_rotation_params, devices.serial_stages
    )
    LOGGER.info("Setup zebra for collection in the positive direction and arm")
    yield from setup_zebra_for_collection(
        devices.zebra,
        RotationDirection.POSITIVE,
        parameters.zebra_rotation_params.ramp_start,
        gate_width,
        pulse_width,
    )
    yield from arm_zebra(devices.zebra)
    yield from bps.abs_set(
        devices.diffractometer.phi,
        parameters.zebra_rotation_params.scan_end_deg,
        wait=True,
    )
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(devices.zebra)
    yield from setup_sample_stage(
        parameters.zebra_rotation_params,
        devices.serial_stages,
    )
    LOGGER.info("Setup zebra for collection in the negative direction and arm")
    yield from setup_zebra_for_collection(
        devices.zebra,
        RotationDirection.NEGATIVE,
        parameters.zebra_rotation_params.ramp_start,
        gate_width,
        pulse_width,
    )
    yield from arm_zebra(devices.zebra)
    yield from bps.abs_set(
        devices.diffractometer.phi, parameters.rot_axis_start, wait=True
    )
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(devices.zebra)


def abort_zebra(diffractometer: FourCircleDiffractometer, zebra: Zebra) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_zebra(zebra)


def run_zebra_test(
    gate_width: float,
    pulse_width: float,
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2ZebraComposite = inject(),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_zebra(
            gate_width,
            pulse_width,
            devices,
            parameters,
        ),
        except_plan=lambda: (
            yield from abort_zebra(devices.diffractometer, devices.zebra)
        ),
        final_plan=lambda: (
            yield from move_sample_stage_back(
                devices.serial_stages, parameters.zebra_rotation_params.scan_start_deg
            )
        ),
        auto_raise=False,
    )
