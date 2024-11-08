from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.tasks import start_analysis_task
from app.schemas.api import AnalyzeUrlRequest, AnalyzeUrlResponse, AnalysisResultResponse

router = APIRouter()


@router.post("/analyze/", response_model=AnalyzeUrlResponse)
async def analyze_url(request: AnalyzeUrlRequest) -> AnalyzeUrlResponse:
    task = start_analysis_task.delay(request.url)
    return AnalyzeUrlResponse(task_id=task.id, status="processing")


@router.get("/analyze/{task_id}", response_model=AnalysisResultResponse)
async def get_analysis_result(task_id: str) -> AnalysisResultResponse:
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return AnalysisResultResponse(status="processing")
    elif task_result.state == "SUCCESS":
        return AnalysisResultResponse(status="completed", result=task_result.result)
    elif task_result.state == "FAILURE":
        return AnalysisResultResponse(status="failed")
    else:
        return AnalysisResultResponse(status=task_result.state)
