"""Entry point plans that use access controlled devices to operate the optics
from one of the hutches."""

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.access_controlled.attenuator_motor_squad import (
    AttenuatorMotorPositions,
    AttenuatorMotorSquad,
)
from dodal.devices.beamlines.i19.access_controlled.energy_device import (
    AccessControlledEnergyComposite,
)
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.beamlines.i19.access_controlled.shutter import (
    AccessControlledShutter,
)
from dodal.devices.hutch_shutter import ShutterDemand

from i19_bluesky.log import LOGGER


def apply_attenuator_positions(
    position_demands: AttenuatorMotorPositions,
    motor_squad: AttenuatorMotorSquad = inject("attenuator_motor_squad"),
) -> MsgGenerator[None]:
    validated_demands = position_demands.validated_and_complete()
    LOGGER.info(f"Applying position demands {validated_demands} to attenuator elements")
    yield from bps.abs_set(motor_squad, position_demands, wait=True)


def apply_voltage_to_piezo_actuators(
    requested_voltage: float, piezo_device: AccessControlledPiezoActuator
) -> MsgGenerator[None]:
    """Apply new voltage to the requested piezo actuator on the focus mirror."""
    LOGGER.info(f"Applying {requested_voltage} to {piezo_device.name}")
    yield from bps.abs_set(piezo_device, requested_voltage, wait=True)


def change_energy(
    requested_energy: float,
    energy_device: AccessControlledEnergyComposite = inject("energy_device"),
) -> MsgGenerator[None]:
    """Trigger a plan to change the energy to the requested value.
    The triggered plan will change the energy on the dcm, move the undulator gap, set
    the mirror stripes and then apply a new voltage to the piezos. The values for this
    can be found in i19-shared/json.

    Args:
        requested_energy: The newenergy to set, in KeV.
    """
    LOGGER.info(f"Changing the energy to {requested_energy} KeV.")
    yield from bps.abs_set(energy_device, requested_energy, wait=True)


def open_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to open the shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.OPEN, wait=True)


def close_experiment_shutter(
    shutter: AccessControlledShutter = inject("shutter"),
) -> MsgGenerator[None]:
    LOGGER.debug("Send command to close the shutter.")
    yield from bps.abs_set(shutter, ShutterDemand.CLOSE, wait=True)
