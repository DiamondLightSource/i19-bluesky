import os
from pathlib import Path
from typing import Any

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.common.beamlines.beamline_utils import get_path_provider, set_path_provider
from dodal.common.visit import LocalDirectoryServiceClient, StaticVisitPathProvider
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from ophyd_async.core import Device, DeviceVector, init_devices, set_mock_value
from ophyd_async.epics.core import epics_signal_rw
from ophyd_async.fastcs.panda import HDFPanda

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
    return diffractometer
