import pytest
from blueapi.core import BlueskyContext
from bluesky.run_engine import RunEngine
from dodal.devices.hutch_shutter import (
    HutchShutter,
    ShutterDemand,
    ShutterState,
)
from dodal.devices.i19.access_controlled.hutch_access import HutchAccessControl
from ophyd_async.core import set_mock_value

from i19_bluesky.exceptions import HutchInvalidError
from i19_bluesky.optics.experiment_shutter_plans import (
    operate_shutter_plan,
)
from i19_bluesky.parameters.components import HutchName


@pytest.mark.parametrize(
    "active_hutch, request_hutch, shutter_demand, start_state, expected_state",
    [
        (
            "EH1",
            HutchName.EH1,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.OPEN,
        ),
        (
            "EH1",
            HutchName.EH1,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.CLOSED,
        ),
        (
            "EH2",
            HutchName.EH2,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.OPEN,
        ),
        (
            "EH2",
            HutchName.EH2,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.CLOSED,
        ),
    ],
)
async def test_hutch_shutter_opens_and_closes_if_run_by_active_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    start_state: ShutterState,
    expected_state: ShutterState,
    shutter_demand: ShutterDemand,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(expt_shutter.status, start_state)
    RE(
        operate_shutter_plan(
            request_hutch, access_control_device, shutter_demand, expt_shutter
        )
    )

    assert await expt_shutter.status.get_value() == expected_state


@pytest.mark.parametrize(
    "active_hutch, request_hutch, shutter_demand, start_state, expected_state",
    [
        (
            "EH1",
            HutchName.EH2,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.CLOSED,
        ),
        (
            "EH1",
            HutchName.EH2,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.OPEN,
        ),
        (
            "EH2",
            HutchName.EH1,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.CLOSED,
        ),
        (
            "EH2",
            HutchName.EH1,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.OPEN,
        ),
    ],
)
async def test_hutch_shutter_does_not_operate_from_wrong_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    shutter_demand: ShutterDemand,
    start_state: ShutterState,
    expected_state: ShutterState,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(expt_shutter.status, start_state)
    RE(
        operate_shutter_plan(
            request_hutch,
            access_control_device,
            shutter_demand,
            expt_shutter,
        )
    )

    assert await expt_shutter.status.get_value() == expected_state


@pytest.mark.parametrize(
    "request_hutch, shutter_demand",
    [
        (HutchName.EH1, ShutterDemand.OPEN),
        (HutchName.EH2, ShutterDemand.CLOSE),
    ],
)
def test_operate_hutch_shutter_raises_error_if_hutch_invalid(
    request_hutch: HutchName,
    shutter_demand: ShutterDemand,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, "INVALID")
    with pytest.raises(HutchInvalidError):
        RE(
            operate_shutter_plan(
                request_hutch, access_control_device, shutter_demand, expt_shutter
            )
        )


def test_signature_of_shutter_plan(context: BlueskyContext):
    plan = operate_shutter_plan
    context.register_plan(plan)
    assert plan.__name__ in context.plans

    schema = context.plans["operate_shutter_plan"].model.model_json_schema()

    # Plan
    assert schema["title"] == "operate_shutter_plan"

    # Check arguments
    assert "experiment_hutch" in schema["properties"].keys()
    assert "access_device" in schema["properties"].keys()
    assert "shutter_demand" in schema["properties"].keys()
    assert "shutter" in schema["properties"].keys()

    # Check required arguments - shutter missing because injected
    assert "shutter" not in schema["required"]
    assert schema["required"] == [
        "experiment_hutch",
        "access_device",
        "shutter_demand",
    ]
