from pathlib import Path

import pytest

from i19_bluesky.parameters.components import (
    HutchName,
    PandaRotationParams,
    RotationParams,
    VisitParameters,
    ZebraRotationParams,
)


@pytest.mark.parametrize("hutch", ["EH1", "EH2"])
def test_validate_visit_parameters_model(hutch):
    model = {
        "hutch": hutch,
        "visit": "/tmp/foo",
        "dataset": "bar",
        "filename_prefix": "some_file",
    }
    VisitParameters.model_validate(model)


def test_visit_parameters():
    model = {
        "hutch": HutchName.EH2,
        "visit": "/tmp/foo",
        "dataset": "bar",
        "filename_prefix": "some_file",
    }

    params = VisitParameters(**model)

    assert isinstance(params.visit, Path)
    assert params.collection_directory == Path("/tmp/foo/bar")


def test_validate_rotation_parameters_model():
    model = {
        "rotation_axis": "omega",
        "scan_start_deg": -90,
        "scan_increment_deg": 0.1,
        "scan_steps": 10,
    }

    RotationParams.model_validate(model)


def test_rotation_parameters():
    model = {
        "rotation_axis": "phi",
        "scan_start_deg": -10,
        "scan_increment_deg": 0.2,
        "scan_steps": 10,
        "exposure_time_s": 0.1,
    }

    params = RotationParams(**model)

    assert params.scan_end_deg == -8.0
    assert params.oscillation == 2.0
    assert params.oscillation_time == 1.0
    assert params.rotation_axis_velocity == 2.0


def test_zebra_rotation_parameters():
    model = {
        "rotation_axis": "phi",
        "scan_start_deg": -10,
        "scan_increment_deg": 0.2,
        "scan_steps": 10,
        "exposure_time_s": 0.1,
    }
    params = ZebraRotationParams(**model)

    assert params.rotation_direction == "Positive"
    assert params.ramp_start == -10.5
    assert params.ramp_end == -7.5


def test_panda_rotation_parameters():
    model = {
        "rotation_axis": "phi",
        "scan_start_deg": -10,
        "scan_increment_deg": 0.2,
        "scan_steps": 10,
        "exposure_time_s": 0.1,
        "ramp_distance_deg": 0.4,
    }

    params = PandaRotationParams(**model)

    assert params.ramp_distance_deg == 0.4
