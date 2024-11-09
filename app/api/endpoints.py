from typing import Dict

from celery.result import AsyncResult
from fastapi import APIRouter

from app.schemas.api import (AnalysisResultResponse, AnalyzeUrlRequest,
                             AnalyzeUrlResponse)
from app.tasks import start_analysis_task

router = APIRouter()


@router.post("/analyze/", response_model=AnalyzeUrlResponse)
async def analyze_url(request: AnalyzeUrlRequest) -> AnalyzeUrlResponse:
    task_ids: Dict[str, str] = {}
    for url in set(request.urls):
        task = start_analysis_task.delay(url, request.validate_params)
        task_ids[url] = task.id
    return AnalyzeUrlResponse(task_ids=task_ids, status="processing")


@router.get("/analyze/{task_id}", response_model=AnalysisResultResponse)
async def get_analysis_result(task_id: str) -> AnalysisResultResponse:
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return AnalysisResultResponse(status="processing", result=None)
    elif task_result.state == "SUCCESS":
        return AnalysisResultResponse(status="completed", result=task_result.result)
    elif task_result.state == "FAILURE":
        return AnalysisResultResponse(status="failed", result=None)
    else:
        return AnalysisResultResponse(status=task_result.state, result=None)
