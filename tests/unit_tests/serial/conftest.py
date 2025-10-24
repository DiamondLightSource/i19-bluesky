import pytest
from ophyd_async.core import Device, DeviceVector, SignalRW
from ophyd_async.fastcs.core import fastcs_connector
from ophyd_async.fastcs.panda import PandaBitMux, PulseBlock


@pytest.fixture
async def panda():
    class PulseBlockWithEnable(PulseBlock):
        enable: SignalRW[PandaBitMux]

    class TestPanda(Device):
        pulse: DeviceVector[PulseBlockWithEnable]
        seq: DeviceVector[PulseBlockWithEnable]

        def __init__(self, uri: str, name: str = ""):
            super().__init__(name=name, connector=fastcs_connector(self, uri))

    mock_panda = TestPanda("PANDA")
    await mock_panda.connect(mock=True)
    return mock_panda
