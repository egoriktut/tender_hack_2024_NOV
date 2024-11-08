from app.celery_app import celery_app
from app.scraper import fetch_and_parse
from app.ai_model import ModelInference
from app.config import settings
from typing import Dict, Any

model_inference = ModelInference(settings.MODEL_PATH)

@celery_app.task
def start_analysis_task(url: str) -> Dict[str, Any]:
    """
    This task fetches and parses content from a URL, then runs it through an AI model for analysis.

    :param url: URL to fetch and analyze.
    :return: A dictionary containing the URL and the analysis result.
    """
    page_data = fetch_and_parse(url)  # Assuming `fetch_and_parse` returns a dict with 'content' key
    analysis_result = model_inference.validate_content(page_data["content"])

    return {"url": url, "analysis": analysis_result}
