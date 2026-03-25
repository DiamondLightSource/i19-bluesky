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
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.serial.run_serial_with_panda import (
    run_serial_with_panda,
    setup_then_trigger_panda,
)


@pytest.mark.parametrize(
    "params,detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time,eh2_aperture",
    [
        (
            {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12],
                5: [13, 14, 15],
            },
            50,
            30,
            50,
            60,
            0.5,
            0.2,
            PinColRequest.PCOL20,
        ),
        (
            {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12],
                5: [13, 14, 15],
            },
            80,
            90,
            50,
            60,
            0.5,
            0.2,
            PinColRequest.PCOL100,
        ),
    ],
)
@patch("i19_bluesky.serial.run_serial_with_panda.move_diffractometer_back")
@patch("i19_bluesky.serial.run_serial_with_panda.setup_then_trigger_panda")
async def test_run_serial_with_panda(
    mock_setup_then_trigger_panda: MagicMock,
    mock_move_diffractometer_back: MagicMock,
    params: dict,
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
    RE(
        run_serial_with_panda(
            params,
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
    "params,detector_z,detector_two_theta,phi_start,phi_end,phi_steps,exposure_time,eh2_aperture",
    [
        (
            {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12],
                5: [13, 14, 15],
            },
            50.0,
            30,
            50.0,
            60,
            1,
            0.2,
            PinColRequest.PCOL20,
        ),
        (
            {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12],
                5: [13, 14, 15],
            },
            80.0,
            90,
            50.0,
            60,
            1,
            0.2,
            PinColRequest.PCOL100,
        ),
    ],
)
@patch("i19_bluesky.serial.run_serial_with_panda.setup_beamline_before_collection")
@patch("i19_bluesky.serial.run_serial_with_panda.trigger_panda")
async def test_setup_then_trigger_panda(
    mock_trigger_panda: MagicMock,
    mock_setup_beamline_before_collection: MagicMock,
    params: dict,
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
    eh2_eiger: EigerDetector,
    RE: RunEngine,
):
    RE(
        setup_then_trigger_panda(
            params,
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
            eh2_eiger,
        )
    )
    mock_setup_beamline_before_collection.assert_called_once_with(
        detector_z,
        detector_two_theta,
        eh2_aperture,
        eh2_backlight,
        eh2_diffractometer,
        pincol,
    )
    mock_trigger_panda.assert_called_once_with(
        params,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
        eh2_diffractometer,
        mock_panda,
        eh2_eiger,
    )
