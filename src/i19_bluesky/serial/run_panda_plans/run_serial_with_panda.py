import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    end_run,
    run_on_collection_abort,
    trigger_panda,
)
from i19_bluesky.serial.setup_beamline_plans.setup_beamline_pre_collection import (
    setup_beamline_before_collection,
)


def setup_then_trigger_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment.
    Has contingencies to abort if any stage produces errors, before moving the
    diffractometer to its starting position. Designed to be called with BlueAPI.

    Args:
        parameters (SerialExperimentEh2): SerialExperimentEh2 object
        devices (SerialCollectionEh2PandaComposite): SerialCollectionEh2PandaComposite \
        object
    """

    yield from setup_beamline_before_collection(parameters, devices)
    yield from trigger_panda(parameters, devices)


@bpp.run_decorator()
def run_serial_with_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        setup_then_trigger_panda(parameters, devices),
        except_plan=lambda: (yield from run_on_collection_abort(devices)),
        final_plan=lambda: (yield from end_run(parameters, devices)),
        auto_raise=False,
    )
