from app.celery_app import celery_app
from app.scraper import fetch_and_parse
from app.ai_model import ModelInference
from app.config import settings
from typing import Dict, Any, List
from app.schemas.api import ValidationOption, AnalyzeUrlRequest

model_inference = ModelInference(settings.MODEL_PATH)

@celery_app.task
def start_analysis_task(url: str, validate_params: List[ValidationOption]) -> Dict[str, Any]:

    """
    This task fetches and parses content from a URL, then runs it through an AI model for analysis.

    :param url: URL to fetch and analyze.
    :return: A dictionary containing the URL and the analysis result.
    """
    page_data = fetch_and_parse(url)  # Assuming `fetch_and_parse` returns a dict with 'content' key
    if page_data is not None:
        raise Exception()
    analysis_result = model_inference.validate_content(page_data, validate_params)

    return {"url": url, "analysis": analysis_result}
