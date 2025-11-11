from abc import abstractmethod
from enum import StrEnum

from dodal.devices.zebra.zebra import RotationDirection
from pydantic import BaseModel, Field

from i19_bluesky.parameters.components import RotationAxis, VisitParameters


class GridType(StrEnum):
    POLYMER = "polymer"
    SILICON = "silicon"
    KAPTON400 = "kapton"
    FILM = "film"


class RotationParameters(BaseModel):
    # This might need adjusting to account for successive backwards and forwards
    # Essentially: for eh1/zebra only in pne direction, for eh2/panda need a series of
    # both. Or something
    rotation_axis: RotationAxis = Field(default=RotationAxis.PHI)
    scan_start_deg: float = Field(default=0)
    scan_increment_deg: float = Field(default=0.1, gt=0)
    scan_width_deg: float = Field(default=0, gt=0)
    rotation_direction: RotationDirection = Field(default=RotationDirection.POSITIVE)


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
    def tot_num_windows(self) -> int:
        return self.x_steps * self.z_steps


class SerialExperiment(VisitParameters):
    """General, for both hutches"""

    grid: GridParameters
    transmission_fraction: float

    @property
    @abstractmethod
    def detector_params(self):
        pass


class SerialExperimentInEh2(SerialExperiment):
    pass
