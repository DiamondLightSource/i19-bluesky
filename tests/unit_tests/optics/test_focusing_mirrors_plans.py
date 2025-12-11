import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.i19.access_controlled.hutch_access import HutchAccessControl
from ophyd_async.core import set_mock_value

from i19_bluesky.optics.focusing_mirrors_plans import apply_voltage_to_vfm_piezo
from i19_bluesky.parameters.components import HutchName


@pytest.mark.parametrize("active_hutch, voltage", [("EH1", 1.2), ("EH2", 3.6)])
async def test_apply_voltage_to_vfm_piezo(
    active_hutch: str,
    voltage: float,
    access_control_device: HutchAccessControl,
    vfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    RE(
        apply_voltage_to_vfm_piezo(
            HutchName[active_hutch], access_control_device, voltage, vfm
        )
    )

    assert await vfm.piezo.get_value() == voltage


@pytest.mark.parametrize(
    "active_hutch, request_hutch, voltage",
    [("EH1", HutchName.EH2, 1.5), ("EH2", HutchName.EH1, 3.6)],
)
async def test_voltage_not_applied_to_vfm_piezo_from_wrong_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    voltage: float,
    access_control_device: HutchAccessControl,
    vfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    RE(apply_voltage_to_vfm_piezo(request_hutch, access_control_device, voltage, vfm))

    assert await vfm.piezo.get_value() == 1.0


@pytest.mark.parametrize("active_hutch, voltage", [("EH1", 0.5), ("EH2", 2.4)])
async def test_apply_voltage_to_hfm_piezo(
    active_hutch: str,
    voltage: float,
    access_control_device: HutchAccessControl,
    hfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    RE(
        apply_voltage_to_vfm_piezo(
            HutchName[active_hutch], access_control_device, voltage, hfm
        )
    )

    assert await hfm.piezo.get_value() == voltage


@pytest.mark.parametrize(
    "active_hutch, request_hutch, voltage",
    [("EH1", HutchName.EH2, 0.5), ("EH2", HutchName.EH1, 2.4)],
)
async def test_voltage_not_applied_to_hfm_piezo_from_wrong_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    voltage: float,
    access_control_device: HutchAccessControl,
    hfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    RE(apply_voltage_to_vfm_piezo(request_hutch, access_control_device, voltage, hfm))

    assert await hfm.piezo.get_value() == 3.0
