import os
from typing import Any

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.common.beamlines.beamline_utils import get_path_provider, set_path_provider
from dodal.common.visit import LocalDirectoryServiceClient, StaticVisitPathProvider
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.core import Device, DeviceVector, init_devices, set_mock_value
from ophyd_async.epics.core import epics_signal_rw
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.parameters.components import HutchName, Path
from i19_bluesky.parameters.serial_parameters import (
    DetectorType,
    DeviceInput,
    GridParameters,
    GridType,
    SerialExperiment,
)

set_path_provider(
    StaticVisitPathProvider(
        "ixx",
        Path(os.path.dirname(__file__)),
        client=LocalDirectoryServiceClient(),
    )
)


@pytest.fixture
async def mock_panda() -> HDFPanda:
    async with init_devices(connect=True, mock=True):
        mock_panda = HDFPanda(
            prefix="ixx-test-panda", path_provider=get_path_provider()
        )

    class MockBlock(Device):
        def __init__(
            self,
            prefix: str,
            name: str = "",
            attributes: dict[str, Any] = {},  # noqa
        ):
            for name, dtype in attributes.items():
                setattr(self, name, epics_signal_rw(dtype, "", ""))
            super().__init__(name)

    async def set_mock_blocks(
        panda, mock_blocks: dict[str, tuple[int, dict[str, Any]]]
    ):
        for name, block in mock_blocks.items():
            n, attrs = block
            block = mock_vector_block(n, attrs)
            await block.connect(mock=True)
            setattr(panda, name, block)

    def mock_vector_block(n, attributes):
        return DeviceVector(
            {i: MockBlock(f"{i}", f"{i}", attributes) for i in range(n)}
        )

    async def create_mock_signals(devices_and_signals: dict[Device, dict[str, Any]]):
        for device, signals in devices_and_signals.items():
            for name, dtype in signals.items():
                sig = epics_signal_rw(dtype, name, name)
                await sig.connect(mock=True)
                setattr(device, name, sig)

    await set_mock_blocks(
        mock_panda,
        {
            "inenc": (8, {"val": float, "setp": float}),
            "outenc": (8, {"val": str}),
        },
    )

    await create_mock_signals(
        {
            mock_panda.pcap: {"enable": str},
            **{mock_panda.pulse[i]: {"enable": str} for i in mock_panda.pulse.keys()},
        }
    )

    return mock_panda


@pytest.fixture
async def eh2_diffractometer(RE: RunEngine) -> FourCircleDiffractometer:
    diffractometer = i19_2.diffractometer.build(connect_immediately=True, mock=True)
    set_mock_value(diffractometer.phi.velocity, 1)
    set_mock_value(diffractometer.det_stage.det_z.user_readback, 100)
    set_mock_value(diffractometer.det_stage.two_theta.user_readback, 0)
    set_mock_value(diffractometer.phi.user_readback, 0)
    return diffractometer


@pytest.fixture
async def pincol(RE: RunEngine) -> PinholeCollimatorControl:
    pincol = i19_2.pinhole_and_collimator.build(connect_immediately=True, mock=True)
    set_mock_value(pincol.mapt.pin_x_out, 30.0)
    set_mock_value(pincol.mapt.col_x_out, 20.0)
    return pincol


@pytest.fixture
async def eh2_backlight(RE: RunEngine) -> BacklightPosition:
    backlight = BacklightPosition("", name="mock_backlight")
    await backlight.connect(mock=True)
    return backlight


@pytest.fixture
async def eh2_eiger(RE: RunEngine) -> EigerDetector:
    eiger = EigerDetector(prefix="ixx-test-eiger", path_provider=get_path_provider())
    return eiger


@pytest.fixture
async def devices(
    mock_panda, eh2_eiger, eh2_backlight, eh2_diffractometer, pincol
) -> DeviceInput:
    devices = DeviceInput(
        diffractometer=eh2_diffractometer,
        backlight=eh2_backlight,
        pincol=pincol,
        panda=mock_panda,
        eiger=eh2_eiger,
    )

    return devices


@pytest.fixture
def dummy_wells_settings():
    return {
        "first": 0,
        "last": 5,
        "selected": [1, 3, 5],
        "series_length": 3,
        "manual_selection_enabled": True,
    }


@pytest.fixture
def parameters(dummy_wells_settings):
    return SerialExperiment(
        hutch=HutchName.EH2,
        visit=Path("/tmp/i19-2/cm12345-1"),
        dataset="foo",
        filename_prefix="bar_01",
        images_per_well=10,
        exposure_time_s=0.1,
        image_width_deg=0.1,
        detector_distance_mm=320,
        two_theta_deg=0,
        transmission_fraction=0.3,
        grid=GridParameters(
            grid_type=GridType.SILICON,
            x_steps=20,
            z_steps=20,
        ),
        aperture_request=PinColRequest.PCOL100,
        detector_type=DetectorType.EIGER,
        well_position={1: (1, 2, 3)},
        wells=dummy_wells_settings,
        rot_axis_start=-5,
        rot_axis_increment=0.1,
        rot_axis_end=10,
    )
