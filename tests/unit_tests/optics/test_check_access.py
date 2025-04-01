import bluesky.plan_stubs as bps
from blueapi.core import BlueskyContext
from bluesky.utils import MsgGenerator

from i19_bluesky.optics.check_access_control import check_access


def test_plan_signature_with_check_access(context: BlueskyContext):
    @check_access
    def dummy_plan(seconds: float) -> MsgGenerator:
        yield from bps.sleep(seconds)

    plan = dummy_plan
    context.register_plan(plan)
    assert plan.__name__ in context.plans

    schema = context.plans["dummy_plan"].model.model_json_schema()

    # Check arguments
    assert "seconds" in schema["properties"].keys()
    assert "access_device" in schema["properties"].keys()
    assert "experiment_hutch" in schema["properties"].keys()

    assert schema["required"] == [
        "experiment_hutch",
        "access_device",
        "seconds",
    ]
