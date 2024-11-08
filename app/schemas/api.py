from pydantic import BaseModel
from typing import Optional, Dict, Any


class AnalyzeUrlRequest(BaseModel):
    url: str


class AnalyzeUrlResponse(BaseModel):
    task_id: str
    status: str


class AnalysisResultResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
