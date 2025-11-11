from enum import StrEnum

from pydantic import BaseModel


class HutchName(StrEnum):
    EH1 = "EH1"
    EH2 = "EH2"


class VisitParams(BaseModel):
    pass
