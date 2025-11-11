from dodal.devices.zebra.zebra import RotationDirection
from pydantic import BaseModel, Field

from i19_bluesky.parameters.components import RotationAxis, VisitParameters


class RotationParameters(BaseModel):
    rotation_axis: RotationAxis = Field(default=RotationAxis.PHI)
    scan_start_deg: float
    scan_width_deg: float
    rotation_direction: RotationDirection = Field(default=RotationDirection.POSITIVE)


class GridParameters(BaseModel):
    grid_type: str


class SerialExperiment(VisitParameters):
    transmission_fraction: float
