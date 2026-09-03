# from abc import abstractmethod

from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
)
from pydantic import computed_field

from i19_bluesky.parameters.components import (
    DetectorType,
    HutchName,
    PandaRotationParams,
    RotationAxis,
    VisitParameters,
    ZebraRotationParams,
)
from i19_bluesky.parameters.constants import DetectorConstants, EigerConstants


class SerialExperiment(VisitParameters):
    """General, for both hutches"""

    images_per_well: int
    exposure_time_s: float
    image_width_deg: float
    detector_distance_mm: float
    two_theta_deg: float
    transmission_fraction: float
    wells_to_collect: dict[str, tuple]
    wells_series_len: int  # how many wells to collect each arm
    rot_axis_start: float
    rot_axis_increment: float
    rotation_axis: RotationAxis = RotationAxis.PHI

    @property
    def total_num_wells(self) -> int:
        return len(self.wells_to_collect)

    @computed_field
    @property
    def total_num_images(self) -> int:
        return self.images_per_well * self.total_num_wells

    def split_wells_per_run(self) -> list[dict]:
        """Divide wells into run list: each to be collected in one detector arm."""
        wells = list(self.wells_to_collect.items())
        run_list = [
            dict(wells[i : i + self.wells_series_len])
            for i in range(0, self.total_num_wells, self.wells_series_len)
        ]
        return run_list

    # @property
    # @abstractmethod
    # def detector_params(self): ...
    # TODO see https://github.com/DiamondLightSource/i19-bluesky/issues/103


class SerialExperimentEh2(SerialExperiment):
    aperture_request: PinColRequest
    detector_type: DetectorType
    hutch: HutchName = HutchName.EH2

    @property
    def zebra_rotation_params(self) -> ZebraRotationParams:
        return ZebraRotationParams(
            rotation_axis=self.rotation_axis,
            scan_start_deg=self.rot_axis_start,
            scan_increment_deg=self.rot_axis_increment,
            scan_steps=self.images_per_well,
            exposure_time_s=self.exposure_time_s,
            # Assumes rotation starts positive
        )

    @property
    def panda_rotation_params(self) -> PandaRotationParams:
        return PandaRotationParams(
            rotation_axis=self.rotation_axis,
            scan_start_deg=self.rot_axis_start,
            scan_increment_deg=self.rot_axis_increment,
            scan_steps=self.images_per_well,
            exposure_time_s=self.exposure_time_s,
        )

    @property
    def detector_constants(self) -> EigerConstants:
        match self.detector_type:
            case DetectorType.EIGER:
                return DetectorConstants.EIGER
