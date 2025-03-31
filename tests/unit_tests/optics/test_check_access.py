import bluesky.plan_stubs as bps
import pytest
from blueapi.core import BlueskyContext
from bluesky.utils import MsgGenerator

from i19_bluesky.optics.check_access_control import HutchName
from i19_bluesky.optics.experiment_shutter_plans import operate_shutter_plan


@pytest.fixture
def context() -> BlueskyContext:
    return BlueskyContext()


def test_signature_of_plan_with_check_access(context: BlueskyContext):
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


def test_register_plan_with_enum(context: BlueskyContext):
    def my_plan(hutch: HutchName) -> MsgGenerator:
        yield from bps.sleep(0.5)

    context.register_plan(my_plan)
    assert my_plan.__name__ in context.plans
