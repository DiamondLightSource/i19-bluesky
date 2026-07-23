import bluesky.plan_stubs as bps
from daq_config_server.models.lookup_tables import DetectorXYLookupTable
from dodal.common.beamlines.beamline_utils import (
    get_config_client,
)
from dodal.devices.detector.det_dim_constants import DetectorSize, DetectorSizeConstants
from dodal.devices.util.lookup_tables import linear_interpolation_lut
from ophyd_async.fastcs.eiger import EigerDetector

from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2

BEAM_XY_TABLE_PATH = (
    "/dls_sw/i19-2/software/daq_configuration/lookup/DetDistToBeamXYConverterE4M.txt"
)


def _convert_beam_centre_to_pixels(
    beam_centre_mm: tuple[float, float],
    image_size_mm: DetectorSize,
    image_size_px: DetectorSize,
) -> tuple[float, float]:
    beam_x_px = beam_centre_mm[0] * image_size_px.width / image_size_mm.width
    beam_y_px = beam_centre_mm[1] * image_size_px.height / image_size_mm.height

    return (beam_x_px, beam_y_px)


def _read_converter_lut():
    config_client = get_config_client()
    lut_contents = config_client.get_file_contents(
        BEAM_XY_TABLE_PATH, DetectorXYLookupTable
    )
    return lut_contents.columns


def calculate_beam_centre_from_lut(
    detector_distance_mm: float, det_size_constants: DetectorSizeConstants
) -> tuple[float, float]:
    """Use the lookup table to find the beam centre position in mm and return it in
    pixels.

    Args:
        detector_distance_mm (float): The detector distance in mm from the parameters.
        det_size_constants (DetectorSizeConstants): The detector size parameters.

    Returns:
        tuple[float, float]: x and y positions of beam centre, in pixels.
    """
    lut_columns = _read_converter_lut()

    interpolate_x = linear_interpolation_lut(lut_columns[0], lut_columns[1])
    beam_x_mm = interpolate_x(detector_distance_mm)
    interpolate_y = linear_interpolation_lut(lut_columns[0], lut_columns[2])
    beam_y_mm = interpolate_y(detector_distance_mm)

    beam_centre_px = _convert_beam_centre_to_pixels(
        (beam_x_mm, beam_y_mm),
        det_size_constants.det_dimension,
        det_size_constants.det_size_pixels,
    )
    return beam_centre_px


def write_eiger_params(
    parameters: SerialExperimentEh2,
    energy: float,
    wavelength: float,
    eiger: EigerDetector,
    wait: bool,
    group: str = "eiger_metadata",
):
    beam_centre = calculate_beam_centre_from_lut(
        parameters.detector_distance_mm,
        parameters.detector_constants.DET_SIZE_CONSTANTS,
    )
    yield from bps.abs_set(eiger.detector.photon_energy, energy, group=group)
    yield from bps.abs_set(
        eiger.detector.detector_distance, parameters.detector_distance_mm, group=group
    )
    yield from bps.abs_set(eiger.detector.beam_center_x, beam_centre[0], group=group)
    yield from bps.abs_set(eiger.detector.beam_center_y, beam_centre[1], group=group)
    yield from bps.abs_set(eiger.detector.omega_start, 0, group=group)
    yield from bps.abs_set(eiger.detector.omega_increment, 0, group=group)
    yield from bps.abs_set(
        eiger.detector.wavelength,  # type:ignore
        wavelength,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.two_theta,  # type:ignore
        parameters.two_theta_deg,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.phi_start,  # type:ignore
        parameters.rot_axis_start,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.phi_increment,  # type:ignore
        parameters.rot_axis_increment,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.chi_start,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.chi_increment,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.kappa_start,  # type:ignore
        0,
        group=group,
    )
    yield from bps.abs_set(
        eiger.detector.kappa_increment,  # type:ignore
        0,
        group=group,
    )
    if wait:
        bps.wait(group)
