import bluesky.plan_stubs as bps
from dodal.devices.i19.pin_tip import PinTipCentreHolder
from dodal.devices.oav.oav_parameters import OAVParameters
from dodal.devices.oav.pin_image_recognition import PinTipDetection
from dodal.plans.device_setup_plans import setup_pin_tip_detection_params

# NOTE In scratch location until daq-config-server added
OAV_CONFIG_JSON = "/dls_sw/i19-1/software/bluesky/OAVCentring.json"


def pin_tip_detection_plan(
    centring_context: str,
    pin_tip_detection: PinTipDetection,
    pin_tip_centre: PinTipCentreHolder,
    oav_config: str = OAV_CONFIG_JSON,
):
    oav_parameters = OAVParameters(centring_context, oav_config)

    yield from setup_pin_tip_detection_params(pin_tip_detection, oav_parameters)

    yield from bps.trigger(pin_tip_detection, wait=True)

    tip_x_y_px = yield from bps.rd(pin_tip_detection.triggered_tip)

    yield from bps.abs_set(
        pin_tip_centre.pin_tip_i, int(tip_x_y_px[0]), group="set_beam_center"
    )
    yield from bps.abs_set(
        pin_tip_centre.pin_tip_j, int(tip_x_y_px[1]), group="set_beam_center"
    )
