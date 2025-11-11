from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, field_validator


class HutchName(StrEnum):
    EH1 = "EH1"
    EH2 = "EH2"


class VisitParameters(BaseModel):
    hutch: HutchName
    visit: Path
    dataset: str
    filename_prefix: str

    @field_validator("visit", mode="before")
    @classmethod
    def _parse_visit(cls, visit: str | Path):
        if isinstance(visit, str):
            return Path(visit)
        return visit

    @property
    def collection_directory(self) -> Path:
        return self.visit / self.dataset
