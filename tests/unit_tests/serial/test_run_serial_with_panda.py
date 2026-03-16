from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.run_serial_with_panda import (
    main_entry_plan,
    setup_then_trigger_panda,
)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time",
    [
        (100, 30, 50, 60, 0.5, 0.2),
        (80, 90, 50, 60, 0.5, 0.2),
        # (301, 90, 50, 60, 0.5, 0.2),
    ],
)
@pytest.mark.parametrize(
    "eh2_aperture",
    [
        (PinColRequest.PCOL20),
        (PinColRequest.PCOL100),
    ],
)
@patch("i19_bluesky.serial.run_serial_with_panda.move_diffractometer_back")
@patch("i19_bluesky.serial.run_serial_with_panda.setup_then_trigger_panda")
@patch("i19_bluesky.serial.run_serial_with_panda.abort_panda")
async def test_main_entry_plan(
    mock_abort_panda: MagicMock,
    mock_setup_then_trigger_panda: MagicMock,
    mock_move_diffractometer_back: MagicMock,
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    RE: RunEngine,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    mock_panda: HDFPanda,
):
    # assert that abort panda is ran if required
    # if detector_z > 300:
    #    raise ValueError
    # This am unsure how to impliment, am looking up ways to trigger wrapper.
    if detector_z > 300:
        with pytest.raises(ValueError):
            RE(
                main_entry_plan(
                    detector_z,
                    detector_two_theta,
                    phi_start,
                    phi_end,
                    phi_steps,
                    exposure_time,
                    eh2_aperture,
                    eh2_diffractometer,
                    eh2_backlight,
                    pincol,
                    mock_panda,
                )
            )
            mock_setup_then_trigger_panda.assert_called_once()
            mock_abort_panda.assert_called_once()
            mock_move_diffractometer_back.assert_called_once_with(
                eh2_diffractometer, phi_start
            )
    else:
        RE(
            main_entry_plan(
                detector_z,
                detector_two_theta,
                phi_start,
                phi_end,
                phi_steps,
                exposure_time,
                eh2_aperture,
                eh2_diffractometer,
                eh2_backlight,
                pincol,
                mock_panda,
            )
        )
    mock_setup_then_trigger_panda.assert_called_once()
    mock_move_diffractometer_back.assert_called_once_with(eh2_diffractometer, phi_start)


@pytest.mark.parametrize(
    "detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time,eh2_aperture",
    [
        (100.0, 30, 50.0, 60, 1, 0.2, PinColRequest.PCOL20),
        (80.0, 90, 50.0, 60, 1, 0.2, PinColRequest.PCOL100),
    ],
)
@patch("i19_bluesky.serial.run_serial_with_panda.setup_beamline_before_collection")
@patch("i19_bluesky.serial.run_serial_with_panda.trigger_panda")
async def test_setup_then_trigger_panda(
    mock_trigger_panda: MagicMock,
    mock_setup_beamline_before_collection: MagicMock,
    detector_z: float,
    detector_two_theta: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    eh2_aperture: PinColRequest,
    eh2_diffractometer: FourCircleDiffractometer,
    eh2_backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    mock_panda: HDFPanda,
    RE: RunEngine,
):
    RE(
        setup_then_trigger_panda(
            detector_z,
            detector_two_theta,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            eh2_aperture,
            eh2_diffractometer,
            eh2_backlight,
            pincol,
            mock_panda,
        )
    )
    mock_setup_beamline_before_collection.assert_called_once()
    mock_trigger_panda.assert_called_once()
