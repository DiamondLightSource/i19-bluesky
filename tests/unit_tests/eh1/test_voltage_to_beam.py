from unittest.mock import MagicMock, patch

from bluesky import RunEngine
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import CentroidFromEpics

from i19_bluesky.eh1.voltage_to_beam_position import (
    apply_voltage_and_read_position,
    measure_piezo_voltages_vs_beam_position,
)
from tests.unit_tests.conftest import fake_generator


@patch("i19_bluesky.eh1.voltage_to_beam_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.eh1.voltage_to_beam_position.bps.sleep")
async def test_apply_and_read(
    mock_sleep: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    centroid_device: CentroidFromEpics,
    RE: RunEngine,
):
    (beam_x, beam_y) = RE(
        apply_voltage_and_read_position(1.2, eh1_hfm_piezo, centroid_device)
    ).plan_result

    mock_apply_voltage_plan.assert_called_once_with(1.2, eh1_hfm_piezo)
    mock_sleep.assert_called_once_with(2.0)
    assert await centroid_device.beam_centre_x.get_value() == beam_x
    assert await centroid_device.beam_centre_y.get_value() == beam_y


@patch("i19_bluesky.eh1.voltage_to_beam_position._save_results_to_file")
@patch("i19_bluesky.eh1.voltage_to_beam_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.eh1.voltage_to_beam_position.apply_voltage_and_read_position")
async def test_measure_voltages_vs_position(
    mock_apply_and_rd: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    mock_save: MagicMock,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    centroid_device: CentroidFromEpics,
    RE: RunEngine,
):
    nudges = [(1, 0.05)]
    mock_apply_and_rd.side_effect = [
        fake_generator((700, 250)),
        fake_generator((690, 255)),
        fake_generator((700, 250)),
        fake_generator((690, 255)),
    ]
    RE(measure_piezo_voltages_vs_beam_position(eh1_vfm_piezo, nudges, centroid_device))

    # Prepare was called
    assert await centroid_device.cc_array_port.get_value() == "OAV1.cam"
    assert await centroid_device.stats.nd_array_port.get_value() == "OAV1.cc"

    # Device triggered
    assert await centroid_device.stats.enable_callbacks.get_value() == "Enable"

    # Measurement taken and saved twice
    assert mock_save.call_count == 2
    assert mock_apply_voltage_plan.call_count == 2
