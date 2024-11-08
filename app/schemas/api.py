from enum import Enum

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ValidationOption(Enum):
    VALIDATE_DATE = 1  # Code 1: Validate Date
    VALIDATE_PRICE = 2  # Code 2: Validate Price
    VALIDATE_EMAIL = 3  # Code 3: Validate Email

    # You can also define a method to get the description for each option
    def description(self) -> str:
        descriptions = {
            1: "Validate Date",
            2: "Validate Price",
            3: "Validate Email"
        }
        return descriptions.get(self.value, "Unknown validation")

class AnalyzeUrlRequest(BaseModel):
    urls: List[str]
    validate_params: List[int]


class AnalyzeUrlResponse(BaseModel):
    task_ids: Dict[str, str]
    status: str


class AnalysisResultResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
