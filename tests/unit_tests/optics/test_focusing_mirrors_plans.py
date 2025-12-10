import pytest
from dodal.beamlines import i19_optics
from i19_bluesky.parameters.components import HutchName
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.i19.access_controlled.hutch_access import HutchAccessControl
from ophyd_async.core import set_mock_value, callback_on_mock_put
from bluesky.run_engine import RunEngine

from i19_bluesky.optics.fosing_mirrors_plans import apply_voltage_to_vfm_piezo

@pytest.fixture
def vfm(RE) ->  FocusingMirrorWithPiezo:
    vfm = i19_optics.vfm(connect_immediately=True, mock=True)

    def set_piezo_voltage(value: float, *args, *kwargs):
        set_mock_value(vfm.piezo_rbv, value)
    
    callback_on_mock_put(vfm.piezo, set_piezo_voltage)
    return vfm


@pytest.mark.parametrize("active_hutch, voltage", [("EH1", 1.2), ("EH2", 3.6)])
async def test_apply_voltage_to_vfm_piezo(
    active_hutch: str,
    voltage: float,
    access_control_device: HutchAccessControl,
    vfm: FocusingMirrorWithPiezo,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(vfm.piezo, 1.0)
    RE(
        apply_voltage_to_vfm_piezo(HutchName[active_hutch], access_control_device, voltage, vfm)
    )

    assert await vfm.piezo_rbv.get_value() == voltage


def test_voltage_not_applied_to_vfm_piezo_from_wrong_hutch():
    pass
