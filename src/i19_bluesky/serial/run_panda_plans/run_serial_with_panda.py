import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.run_panda_plans.panda_serial_collection import (
    end_run,
    run_on_collection_abort,
    trigger_panda_collection,
)
from i19_bluesky.serial.setup_beamline_plans.setup_beamline import (
    setup_eh2_serial_collection,
)


def main_collection_plan(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Run a small rotative serial crystallography collection using the PandA to trigger
    the detector."""
    yield from setup_eh2_serial_collection(parameters, devices)
    yield from trigger_panda_collection(parameters, devices)


@bpp.run_decorator()
def run_serial_with_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        main_collection_plan(parameters, devices),
        except_plan=lambda: (
            yield from run_on_collection_abort(
                devices.panda, devices.eiger, devices.diffractometer
            )
        ),
        final_plan=lambda: (
            yield from end_run(
                parameters.rot_axis_start,
                devices.panda,
                devices.eiger,
                devices.serial_stages,
            )
        ),
        auto_raise=False,
    )
