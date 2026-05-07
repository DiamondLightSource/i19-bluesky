# from abc import abstractmethod

from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
)
from pydantic import computed_field

from i19_bluesky.parameters.components import (
    DetectorType,
    PandaRotationParams,
    RotationAxis,
    VisitParameters,
    ZebraRotationParams,
)


class SerialExperiment(VisitParameters):
    """General, for both hutches"""

    images_per_well: int
    exposure_time_s: float
    image_width_deg: float
    detector_distance_mm: float
    two_theta_deg: float
    transmission_fraction: float
    wells_to_collect: dict[str, tuple]
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

    # @property
    # @abstractmethod
    # def detector_params(self): ...
    # TODO see https://github.com/DiamondLightSource/i19-bluesky/issues/103


class SerialExperimentEh2(SerialExperiment):
    aperture_request: PinColRequest
    detector_type: DetectorType

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
