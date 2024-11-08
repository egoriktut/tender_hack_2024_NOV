from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AnalyzeUrlRequest(BaseModel):
    urls: List[str]


class AnalyzeUrlResponse(BaseModel):
    task_ids: List[str]
    status: str


class AnalysisResultResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
