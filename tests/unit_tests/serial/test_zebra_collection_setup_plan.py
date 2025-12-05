from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.zebra.zebra import RotationDirection, Zebra

from i19_bluesky.serial.zebra_collection_setup_plan import (
    PULSE_START,
    setup_out_triggers,
    setup_zebra_for_collection,
    setup_zebra_for_triggering,
)


@patch("i19_bluesky.serial.zebra_collection_setup_plan.setup_zebra_for_triggering")
@patch("i19_bluesky.serial.zebra_collection_setup_plan.setup_out_triggers")
@pytest.mark.parametrize(
    "rotation_direction", [RotationDirection.POSITIVE, RotationDirection.NEGATIVE]
)
async def test_zebra_collection_setup(
    mock_setup_out_triggers: MagicMock,
    mock_setup_zebra_for_triggering: MagicMock,
    rotation_direction: RotationDirection,
    eh2_zebra: Zebra,
    RE: RunEngine,
):
    inputs_list = (rotation_direction, 100.02, 5.04, 5.0)
    RE(setup_zebra_for_collection(eh2_zebra, *inputs_list, wait=True))
    assert await eh2_zebra.pc.gate_start.get_value() == inputs_list[1]
    assert await eh2_zebra.pc.gate_width.get_value() == inputs_list[2]
    assert await eh2_zebra.pc.num_gates.get_value() == 1

    assert await eh2_zebra.pc.pulse_start.get_value() == PULSE_START
    assert await eh2_zebra.pc.pulse_width.get_value() == inputs_list[3]
    assert await eh2_zebra.pc.pulse_step.get_value() == inputs_list[3] + 0.1

    assert await eh2_zebra.pc.dir.get_value() == inputs_list[0]

    mock_setup_zebra_for_triggering.assert_called_once_with(eh2_zebra)
    mock_setup_out_triggers.assert_called_once_with(eh2_zebra)


async def test_setup_out_triggers(eh2_zebra: Zebra, RE: RunEngine):
    RE(setup_out_triggers(eh2_zebra, wait=True))
    assert (
        await eh2_zebra.output.out_pvs[1].get_value() == eh2_zebra.mapping.sources.OR1
    )
    assert (
        await eh2_zebra.output.out_pvs[2].get_value()
        == eh2_zebra.mapping.sources.PC_PULSE
    )


async def test_zebra_for_triggering(eh2_zebra: Zebra, RE: RunEngine):
    RE(setup_zebra_for_triggering(eh2_zebra, wait=True))
    assert await eh2_zebra.pc.gate_source.get_value() == "Position"
    assert await eh2_zebra.pc.gate_trigger.get_value() == "Enc1"
    assert await eh2_zebra.pc.pulse_source.get_value() == "Time"
