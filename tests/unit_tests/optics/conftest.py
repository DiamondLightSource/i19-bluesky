import pytest
from dodal.beamlines import i19_optics
from dodal.devices.beamlines.i19.access_controlled.hutch_access import (
    HutchAccessControl,
)
from dodal.devices.beamlines.i19.mirror_stripes import MirrorStripes, StripeChoice
from dodal.devices.common_dcm import DoubleCrystalMonochromatorWithDSpacing
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.hutch_shutter import (
    InterlockedHutchShutter,
    ShutterDemand,
    ShutterState,
)
from dodal.devices.undulator import UndulatorInKeV
from dodal.utils import AnyDeviceFactory
from ophyd_async.core import callback_on_mock_put, set_mock_value

from i19_bluesky.optics.device_composites import SetEnergyComposite
from tests.conftest import device_factories_for_beamline


@pytest.fixture(scope="session")
def active_device_factories() -> set[AnyDeviceFactory]:
    return device_factories_for_beamline(i19_optics)


@pytest.fixture
def expt_shutter(RE) -> InterlockedHutchShutter:
    expt_shutter = i19_optics.shutter.build(
        connect_immediately=True,
        mock=True,
    )

    def set_status(value: ShutterDemand, *args, **kwargs):
        value_sta = ShutterState.OPEN if value == "Open" else ShutterState.CLOSED
        set_mock_value(expt_shutter.status, value_sta)

    callback_on_mock_put(expt_shutter.control, set_status)
    return expt_shutter


@pytest.fixture
def access_control_device(RE) -> HutchAccessControl:
    access_control = i19_optics.access_control.build(
        connect_immediately=True, mock=True
    )
    return access_control


@pytest.fixture
def vfm(RE) -> FocusingMirrorWithPiezo:
    vfm = i19_optics.vfm.build(connect_immediately=True, mock=True)
    set_mock_value(vfm.piezo, 1.0)
    return vfm


@pytest.fixture
def hfm(RE) -> FocusingMirrorWithPiezo:
    hfm = i19_optics.hfm.build(connect_immediately=True, mock=True)
    set_mock_value(hfm.piezo, 3.0)
    return hfm


@pytest.fixture
def dcm(RE) -> DoubleCrystalMonochromatorWithDSpacing:
    dcm = i19_optics.dcm.build(connect_immediately=True, mock=True)
    set_mock_value(dcm.energy_in_keV.user_readback, 17.8)
    set_mock_value(dcm.wavelength_in_a.user_readback, 0.6)
    return dcm


@pytest.fixture
def undulator(RE) -> UndulatorInKeV:
    undulator = i19_optics.undulator.build(connect_immediately=True, mock=True)
    return undulator


@pytest.fixture
def mirror_stripes(RE) -> MirrorStripes:
    mirror_stripes = i19_optics.mirror_stripes.build(
        connect_immediately=True, mock=True
    )
    set_mock_value(mirror_stripes.stripe_choice, StripeChoice.EH1_PT)
    return mirror_stripes


@pytest.fixture
def energy_devices(dcm, undulator, mirror_stripes, hfm, vfm) -> SetEnergyComposite:
    return SetEnergyComposite(
        dcm=dcm, undulator=undulator, mirror_stripes=mirror_stripes, hfm=hfm, vfm=vfm
    )
