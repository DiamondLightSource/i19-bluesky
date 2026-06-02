import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.access_controlled.hutch_access import (
    HutchAccessControl,
)
from dodal.devices.beamlines.i19.mirror_stripes import StripeChoice
from ophyd_async.core import set_mock_value

from i19_bluesky.optics.change_energy_plans import change_energy_plan
from i19_bluesky.optics.device_composites import SetEnergyComposite
from i19_bluesky.parameters.components import HutchName


async def test_set_energy():
    pass


async def test_apply_piezo_voltages():
    pass


@pytest.mark.parametrize(
    "active_hutch, request_hutch, energy, stripe, current_stripe",
    [
        ("EH1", HutchName.EH2, 22.4, StripeChoice.EH2_PT, StripeChoice.EH1_RH),
        ("EH2", HutchName.EH1, 8.6, StripeChoice.EH1_SI, StripeChoice.EH2_RH),
    ],
)
async def test_energy_and_stripe_not_changed_if_requested_from_wrong_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    energy: float,
    stripe: StripeChoice,
    current_stripe: StripeChoice,
    access_control_device: HutchAccessControl,
    energy_devices: SetEnergyComposite,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(energy_devices.mirror_stripes.stripe_choice, current_stripe)
    set_mock_value(energy_devices.dcm.energy_in_keV.user_readback, 17.8)
    RE(
        change_energy_plan(
            request_hutch, access_control_device, energy, stripe, energy_devices
        )
    )

    assert await energy_devices.dcm.energy_in_keV.user_readback.get_value() == 17.8
    assert (
        await energy_devices.mirror_stripes.stripe_choice.get_value() == current_stripe
    )


async def test_change_energy_plan():
    pass
