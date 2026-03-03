from collections.abc import Generator

import bluesky.plan_stubs as bps
from bluesky.utils import Msg, MsgGenerator
from dodal.devices.beamlines.i19.pin_tip import PinTipCentreHolder
from dodal.devices.oav.oav_parameters import OAVParameters
from dodal.devices.oav.pin_image_recognition import PinTipDetection, Tip
from dodal.plans.device_setup_plans import setup_pin_tip_detection_params

# NOTE In scratch location until daq-config-server added
OAV_CONFIG_JSON = "/dls_sw/i19-1/software/bluesky/OAVCentring.json"


def save_pin_tip_position(
    pin_tip_position: PinTipCentreHolder,
    tip_xy: Tip,
    group: str = "set-pin-tip-pos",
    wait: bool = True,
):
    """Temporary workaround to save pin tip location to Overlay Centre[X,Y] PVs."""
    yield from bps.abs_set(pin_tip_position.pin_tip_i, int(tip_xy[0]), group=group)
    yield from bps.abs_set(pin_tip_position.pin_tip_j, int(tip_xy[1]), group=group)

    if wait:
        yield from bps.wait(group=group)


def trigger_pin_tip_detection(
    pin_tip_detection: PinTipDetection,
) -> Generator[Msg, None, Tip]:
    """Trigger the pin tip detection device and return the x,y location, in pixels."""
    yield from bps.trigger(pin_tip_detection, wait=True)

    tip_x_y_px = yield from bps.rd(pin_tip_detection.triggered_tip)
    return tip_x_y_px


def pin_tip_detection_plan(
    centring_context: str,
    pin_tip_detection: PinTipDetection,
    pin_tip_position: PinTipCentreHolder,
    oav_config: str = OAV_CONFIG_JSON,
) -> MsgGenerator:
    """Run a plan to get the pin tip from the ophyd_async device.

    - Get the pin detection parameters from the OAVCentring json file
    - Trigger pin tip detection and find the x,y position
    - Save the tip position to the overlay PVs - this is a workaround as it's not
    currently possible to get a plan result back from blueapi.

    The workaround will be removed once this is done
    https://github.com/DiamondLightSource/blueapi/issues/1349
    """
    oav_parameters = OAVParameters(centring_context, oav_config)

    yield from setup_pin_tip_detection_params(pin_tip_detection, oav_parameters)

    tip_x_y_px = yield from trigger_pin_tip_detection(
        pin_tip_detection,
    )

    yield from save_pin_tip_position(pin_tip_position, tip_x_y_px)
