from pathlib import Path

import pytest

from i19_bluesky.parameters.components import PandaRotationParams, ZebraRotationParams
from i19_bluesky.parameters.serial_parameters import (
    GridParameters,
    GridType,
    SerialExperiment,
    SerialExperimentEh2,
    WellsSelection,
)


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
def dummy_serial_params(dummy_wells_settings):
    return {
        "hutch": "EH2",
        "visit": "/tmp/i19-2/cm12345-1",
        "dataset": "foo",
        "filename_prefix": "bar_01",
        "images_per_well": 10,
        "exposure_time_s": 0.1,
        "image_width_deg": 0.1,
        "detector_distance_mm": 320,
        "two_theta_deg": 0,
        "transmission_fraction": 0.3,
        "grid": {
            "grid_type": "Silicon",
            "x_steps": 20,
            "z_steps": 20,
        },
        "wells": dummy_wells_settings,
        "rot_axis_start": -5,
        "rot_axis_increment": 0.1,
    }


@pytest.mark.parametrize(
    "grid_type, steps, expected_step_size, expected_block_size",
    [
        (GridType.POLYMER, (20, 20), (0.120, 0.120), (2.28, 2.28)),
        (GridType.SILICON, (20, 20), (0.125, 0.125), (2.375, 2.375)),
        (GridType.KAPTON400, (20, 20), (0.120, 0.120), (2.28, 2.28)),
        (
            GridType.FILM,
            (20, 20),
            (0.100, 0.100),
            (pytest.approx(1.9, 1e-3), pytest.approx(1.9, 1e-3)),
        ),
    ],
)
def test_grid_parameters(grid_type, steps, expected_step_size, expected_block_size):
    grid_params = GridParameters(
        grid_type=grid_type, x_steps=steps[0], z_steps=steps[1]
    )

    assert grid_params.x_step_size == expected_step_size[0]
    assert grid_params.z_step_size == expected_step_size[1]
    assert grid_params.city_block_x == expected_block_size[0]
    assert grid_params.city_block_z == expected_block_size[1]

    assert grid_params.tot_num_windows == 400


def test_wells_selection(dummy_wells_settings):
    params = WellsSelection(**dummy_wells_settings)

    assert params.num_wells_to_collect == 3
    assert params.num_series == 1


def test_wells_selection_with_multiple_series(dummy_wells_settings):
    dummy_wells_settings["series_length"] = 1

    params = WellsSelection(**dummy_wells_settings)

    assert params.num_series == 3


def test_serial_parameter_model(dummy_serial_params):
    SerialExperiment.model_validate(dummy_serial_params)


def test_serial_parameter_model_for_eh2(dummy_serial_params):
    eh2_params = SerialExperimentEh2(**dummy_serial_params)

    assert eh2_params.tot_num_images == 30
    assert eh2_params.rotation_axis == "phi"
    assert eh2_params.collection_directory == Path("/tmp/i19-2/cm12345-1/foo")

    assert isinstance(eh2_params.zebra_rotation_params, ZebraRotationParams)
    assert isinstance(eh2_params.panda_rotation_params, PandaRotationParams)

    assert eh2_params.zebra_rotation_params.scan_start_deg == eh2_params.rot_axis_start
    assert eh2_params.zebra_rotation_params.rotation_direction == "Positive"
    assert (
        eh2_params.zebra_rotation_params.scan_end_deg
        == eh2_params.rot_axis_start
        + eh2_params.rot_axis_increment * eh2_params.images_per_well
    )

    assert (
        eh2_params.panda_rotation_params.exposure_time_s == eh2_params.exposure_time_s
    )
    assert eh2_params.panda_rotation_params.ramp_distance_deg == 0.5
