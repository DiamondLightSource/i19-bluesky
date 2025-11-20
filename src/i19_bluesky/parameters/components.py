from enum import StrEnum
from pathlib import Path

from dodal.devices.zebra.zebra import RotationDirection
from pydantic import BaseModel, Field, field_validator

RAMP_UP_DEG = 0.5


class HutchName(StrEnum):
    EH1 = "EH1"
    EH2 = "EH2"


class RotationAxis(StrEnum):
    PHI = "phi"
    OMEGA = "omega"


class VisitParameters(BaseModel):
    hutch: HutchName
    visit: Path
    dataset: str
    filename_prefix: str

    @field_validator("visit", mode="before")
    @classmethod
    def _parse_visit(cls, visit: str | Path):
        # NOTE, for now leave like this, with the visit as the full path, but in the
        # future it could just be the instrument session and then the full path can be
        # rebuilt from hutch and year
        if isinstance(visit, str):
            return Path(visit)
        return visit

    @property
    def collection_directory(self) -> Path:
        return self.visit / self.dataset


class RotationParams(BaseModel):
    rotation_axis: RotationAxis = Field(default=RotationAxis.PHI)
    scan_start_deg: float = Field(default=0)
    scan_increment_deg: float = Field(default=0.1, gt=0)  # image width
    scan_steps: int = Field(default=1)  # essentially the number of images
    exposure_time_s: float = Field(default=0.2)

    @property
    def scan_end_deg(self) -> float:
        return self.scan_start_deg + self.scan_increment_deg * self.scan_steps

    @property
    def oscillation(self) -> float:
        return self.scan_steps * self.scan_increment_deg

    @property
    def oscillation_time(self) -> float:
        return self.scan_steps * self.exposure_time_s

    @property
    def rotation_axis_velocity(self) -> float:
        return self.scan_increment_deg / self.exposure_time_s


class ZebraRotationParams(RotationParams):
    rotation_direction: RotationDirection = Field(default=RotationDirection.POSITIVE)

    @property
    def ramp_start(self) -> float:
        return self.scan_start_deg - RAMP_UP_DEG

    @property
    def ramp_end(self) -> float:
        return self.scan_end_deg + RAMP_UP_DEG


class PandaRotationParams(RotationParams):
    ramp_distance_deg: float = Field(default=RAMP_UP_DEG)
