from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.zebra.zebra import RotationDirection, Zebra

from i19_bluesky.eh2.zebra_collection_setup_plan import (
    PULSE_WIDTH,
    setup_zebra_for_collection,
    setup_zebra_for_triggering,
)


@pytest.mark.parametrize(
    "rotation_direction", [RotationDirection.POSITIVE, RotationDirection.NEGATIVE]
)
@patch("i19_bluesky.eh2.zebra_collection_setup_plan.setup_zebra_for_triggering")
async def test_zebra_collection_setup(
    mock_triggering_plan: MagicMock,
    rotation_direction: RotationDirection,
    eh2_zebra: Zebra,
    RE: RunEngine,
):
    inputs_list = (rotation_direction, 5, 0.2, 5.04)
    direction, num_images, gate_start, gate_width = inputs_list
    RE(setup_zebra_for_collection(eh2_zebra, *inputs_list, wait=True))
    assert await eh2_zebra.pc.gate_start.get_value() == gate_start
    assert await eh2_zebra.pc.gate_width.get_value() == gate_width
    assert await eh2_zebra.pc.num_gates.get_value() == num_images

    assert await eh2_zebra.pc.pulse_start.get_value() == gate_start + 0.02
    assert await eh2_zebra.pc.pulse_width.get_value() == PULSE_WIDTH

    assert await eh2_zebra.pc.dir.get_value() == direction

    assert (
        await eh2_zebra.output.out_pvs[1].get_value() == eh2_zebra.mapping.sources.OR1
    )

    mock_triggering_plan.assert_called_once_with(eh2_zebra)


async def test_zebra_for_triggering(eh2_zebra: Zebra, RE: RunEngine):
    RE(setup_zebra_for_triggering(eh2_zebra, wait=True))
    assert await eh2_zebra.pc.gate_source.get_value() == "Position"
    assert await eh2_zebra.pc.gate_trigger.get_value() == "Enc1"
    assert await eh2_zebra.pc.pulse_source.get_value() == "Time"
