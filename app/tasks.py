from typing import Dict, List

from app.validation import KSValidator
from app.celery_app import celery_app
from app.config import settings
from app.schemas.api import Result, ValidationOption
from app.schemas.ks import KSAttributes
from app.scraper import fetch_and_parse

ks_validator = KSValidator(settings.MODEL_PATH)


@celery_app.task
def start_analysis_task(url: str, validate_params: List[ValidationOption]) -> Dict:
    page_data = fetch_and_parse(
        url
    )  # Assuming `fetch_and_parse` returns a dict with 'content' key
    if page_data is None:
        raise Exception()
    analysis_result = ks_validator.validate_content(page_data, validate_params)

    return Result(url=url, analysis=analysis_result).dict()
