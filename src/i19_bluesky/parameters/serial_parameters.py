# from abc import abstractmethod
from enum import StrEnum

import pydantic
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda
from pydantic import BaseModel, computed_field

from i19_bluesky.parameters.components import (
    PandaRotationParams,
    RotationAxis,
    VisitParameters,
    ZebraRotationParams,
)


class GridType(StrEnum):
    POLYMER = "Polymer"
    SILICON = "Silicon"
    KAPTON400 = "Kapton"
    FILM = "Film"


class DetectorType(StrEnum):
    EIGER = "EIGER"


class GridParameters(BaseModel):
    grid_type: GridType

    x_steps: int
    z_steps: int

    @property
    def x_step_size(self) -> float:
        match self.grid_type:
            case GridType.POLYMER | GridType.KAPTON400:
                return 0.120
            case GridType.SILICON:
                return 0.125
            case GridType.FILM:
                return 0.100

    @property
    def z_step_size(self) -> float:
        match self.grid_type:
            case GridType.POLYMER | GridType.KAPTON400:
                return 0.120
            case GridType.SILICON:
                return 0.125
            case GridType.FILM:
                return 0.100

    @property
    def city_block_x(self) -> float:
        return (self.x_steps - 1) * self.x_step_size

    @property
    def city_block_z(self) -> float:
        return (self.z_steps - 1) * self.z_step_size

    @property
    def total_num_wells(self) -> int:
        return self.x_steps * self.z_steps


class WellsSelection(BaseModel):
    first: int
    last: int
    selected: list[int]  # NOTE this is 1-indexed
    series_length: int  # How many in the same detector arm
    manual_selection_enabled: bool = False

    @computed_field
    @property
    def num_series(self) -> int:
        if len(self.selected) % self.series_length == 0:
            return len(self.selected) // self.series_length
        else:
            return len(self.selected) // self.series_length + 1

    @property
    def num_wells_to_collect(self) -> int:
        return len(self.selected)


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class DeviceInput:
    diffractometer: FourCircleDiffractometer
    backlight: BacklightPosition
    pincol: PinholeCollimatorControl
    panda: HDFPanda
    eiger: EigerDetector


class SerialExperiment(VisitParameters):
    """General, for both hutches"""

    images_per_well: int
    exposure_time_s: float
    image_width_deg: float
    detector_distance_mm: float
    two_theta_deg: float
    transmission_fraction: float
    grid: GridParameters
    wells: WellsSelection
    # Missing: , , sample_stage, also axes values
    aperture_request: PinColRequest
    detector_type: DetectorType
    well_position: dict[int, tuple]
    rot_axis_start: float
    rot_axis_increment: float
    rot_axis_end: float
    rotation_axis: RotationAxis = RotationAxis.PHI
    # The other positions can be read from device for now and then set to detector

    @computed_field
    @property
    def total_num_images(self) -> int:
        return self.images_per_well * self.wells.num_wells_to_collect

    # @property
    # @abstractmethod
    # def detector_params(self): ...
    # TODO see https://github.com/DiamondLightSource/i19-bluesky/issues/103


class SerialExperimentEh2(SerialExperiment):
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
