from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.access_controlled.hutch_access import (
    HutchAccessControl,
)
from dodal.devices.beamlines.i19.mirror_stripes import StripeChoice
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from ophyd_async.core import set_mock_value

from i19_bluesky.optics.change_energy_plans import (
    _apply_piezo_voltages,
    change_energy_plan,
)
from i19_bluesky.optics.device_composites import SetEnergyComposite
from i19_bluesky.parameters.components import HutchName

PIEZO_VOLTAGES = {
    StripeChoice.EH1_RH: {"hfm": 1.6, "vfm": 1.72},
    StripeChoice.EH2_PT: {"hfm": 3.55, "vfm": 2.28},
}


async def test_set_energy():
    pass


@pytest.mark.parametrize(
    "stripe_choice, expected_voltages",
    [(StripeChoice.EH1_RH, (1.6, 1.72)), (StripeChoice.EH2_PT, (3.55, 2.28))],
)
async def test_apply_piezo_voltages(
    stripe_choice: StripeChoice,
    expected_voltages: tuple[float, float],
    hfm: FocusingMirrorWithPiezo,
    vfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    with patch(
        "i19_bluesky.optics.change_energy_plans._get_piezo_voltages_to_set_from_config_client"
    ) as mock_get_voltages:
        mock_get_voltages.return_value = PIEZO_VOLTAGES
        RE(_apply_piezo_voltages(stripe_choice, hfm, vfm))
        assert await hfm.piezo.get_value() == expected_voltages[0]
        assert await vfm.piezo.get_value() == expected_voltages[1]


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


@patch("i19_bluesky.optics.change_energy_plans._set_energy")
@patch("i19_bluesky.optics.change_energy_plans.bps.abs_set")
@patch("i19_bluesky.optics.change_energy_plans._apply_piezo_voltages")
async def test_change_energy_plan(
    mock_apply_voltages: MagicMock,
    mock_set: MagicMock,
    mock_set_energy: MagicMock,
    access_control_device: HutchAccessControl,
    energy_devices: SetEnergyComposite,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, "EH1")
    RE(
        change_energy_plan(
            HutchName.EH1,
            access_control_device,
            25.4,
            StripeChoice.EH1_PT,
            energy_devices,
        )
    )

    mock_set_energy.assert_called_once_with(
        25.4, energy_devices.dcm, energy_devices.undulator
    )
    mock_set.assert_called_once_with(
        energy_devices.mirror_stripes.stripe_choice, StripeChoice.EH1_PT, wait=True
    )
    mock_apply_voltages.assert_called_once_with(
        StripeChoice.EH1_PT,
        energy_devices.hfm,
        energy_devices.vfm,
    )
