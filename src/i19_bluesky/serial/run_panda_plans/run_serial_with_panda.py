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
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Run primary setup processes then trigger PandA to collect data from experiment.
    Has contingencies to abort if any stage produces errors, before moving the
    diffractometer to its starting position. Designed to be called with BlueAPI.

    Args:
        parameters (SerialExperimentEh2): SerialExperimentEh2 object
        devices (SerialCollectionEh2PandaComposite): SerialCollectionEh2PandaComposite
        object
    """

    yield from setup_beamline_before_collection(
        parameters.aperture_request,
        parameters.detector_distance_mm,
        parameters.two_theta_deg,
        devices.backlight,
        devices.pincol,
        devices.diffractometer,
    )
    yield from trigger_panda(parameters, devices)


@bpp.run_decorator()
def run_serial_with_panda(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite = inject(),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        setup_then_trigger_panda(parameters, devices),
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
