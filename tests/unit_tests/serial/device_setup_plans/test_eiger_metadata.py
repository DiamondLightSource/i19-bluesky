from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.serial.device_setup_plans.eiger_metadata import (
    read_metadata_from_eiger,
)


async def test_read_metadata_from_eiger(
    eh2_eiger: EigerDetector,
):
    r = await read_metadata_from_eiger(eh2_eiger)
    assert r == {
        "Wavelength": 123.98419299999999,
        "beam_centre_x": 100.0,
        "beam_centre_y": 100.0,
        "chi": 0,
        "chi_increment": 0,
        "detector_distance": 100.0,
        "kappa_increment": 0,
        "omega_increment": 0,
        "omega_position": 0,
    }
