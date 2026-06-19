from pathlib import Path

import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.common.beamlines.beamline_utils import (
    get_config_client,
)
from dodal.devices.beamlines.i19.mirror_stripes import MirrorStripes, StripeChoice
from dodal.devices.common_dcm import DoubleCrystalMonochromatorWithDSpacing
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.undulator import UndulatorInKeV

from i19_bluesky.log import LOGGER
from i19_bluesky.optics.check_access_control import check_access
from i19_bluesky.optics.device_composites import SetEnergyComposite

PIEZO_VOLTAGES_JSON_PATH = Path(
    "/dls_sw/i19-1/software/i19-acquisition/i19-shared/json/PiezoVoltages.json"
)


@check_access
def change_energy_plan(
    energy_in_kev: float,
    stripe_choice: StripeChoice,
    devices: SetEnergyComposite = inject(),
) -> MsgGenerator:
    LOGGER.info(f"Change the energy to {energy_in_kev} KeV")
    yield from _set_energy_and_stripes(
        energy_in_kev,
        stripe_choice,
        devices.dcm,
        devices.undulator,
        devices.mirror_stripes,
    )
    yield from _apply_piezo_voltages(stripe_choice, devices.hfm, devices.vfm)


def _set_energy_and_stripes(
    energy_in_kev: float,
    stripe_choice: StripeChoice,
    dcm: DoubleCrystalMonochromatorWithDSpacing,
    undulator: UndulatorInKeV,
    mirror_stripes: MirrorStripes,
    group: str = "drive-dcm-id-gap-and-stripes",
    wait: bool = True,
):
    LOGGER.info("Drive the dcm energy and ID gap")
    yield from bps.abs_set(undulator, energy_in_kev, group=group)
    yield from bps.abs_set(dcm.energy_in_keV, energy_in_kev, group=group)
    LOGGER.info(f"Drive mirrors to {stripe_choice.value} stripe and set voltages")
    yield from bps.abs_set(mirror_stripes.stripe_choice, stripe_choice, group=group)
    if wait:
        yield from bps.wait(group=group)


def _get_piezo_voltages_to_set_from_config_client() -> dict:
    config_client = get_config_client()
    piezo_voltages = config_client.get_file_contents(
        PIEZO_VOLTAGES_JSON_PATH, desired_return_type=dict
    )
    return piezo_voltages


def _apply_piezo_voltages(
    stripe_choice: StripeChoice,
    hfm: FocusingMirrorWithPiezo,
    vfm: FocusingMirrorWithPiezo,
    group: str = "apply-voltage-to-piezo-actuators",
    wait: bool = True,
):
    piezo_voltages_config = _get_piezo_voltages_to_set_from_config_client()
    voltages_to_set = piezo_voltages_config[stripe_choice.value]
    LOGGER.info(f"Set piezo voltages to: {voltages_to_set}")
    yield from bps.abs_set(hfm.piezo, voltages_to_set["hfm"], group=group)
    yield from bps.abs_set(vfm.piezo, voltages_to_set["vfm"], group=group)
    if wait:
        yield from bps.wait(group=group)
