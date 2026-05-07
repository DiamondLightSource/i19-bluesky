from pathlib import Path

import pytest

from i19_bluesky.parameters.components import PandaRotationParams, ZebraRotationParams
from i19_bluesky.parameters.serial_parameters import (
    SerialExperiment,
    SerialExperimentEh2,
)


@pytest.fixture
def dummy_serial_params():
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
        "wells_to_collect": {"01": (0, 0, 0), "02": (0.1, 0, 0)},
        "rot_axis_start": -5,
        "rot_axis_increment": 0.1,
        "rot_axis_end": 10,
    }


@pytest.fixture
def dummy_serial_params_eh2(dummy_serial_params):
    eh2_spec_params = {
        "aperture_request": "100um",
        "detector_type": "EIGER",
    }
    return {**dummy_serial_params, **eh2_spec_params}


def test_serial_parameter_model_validates(dummy_serial_params):
    SerialExperiment.model_validate(dummy_serial_params)


def test_serial_parameters_eh2_model_validates(dummy_serial_params_eh2):
    SerialExperimentEh2.model_validate(dummy_serial_params_eh2)


def test_serial_parameters(dummy_serial_params):
    params = SerialExperiment(**dummy_serial_params)

    assert params.total_num_wells == 2
    assert params.total_num_images == 20


def test_serial_parameter_model_for_eh2(dummy_serial_params_eh2):
    eh2_params = SerialExperimentEh2(**dummy_serial_params_eh2)

    assert eh2_params.total_num_images == 20
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
