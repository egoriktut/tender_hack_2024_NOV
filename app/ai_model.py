import time
from typing import Dict, Any, Optional, List
from app.schemas.ks import KSAttributes
from app.schemas.api import ValidationOption

class ModelInference:
    def __init__(self, model_path: Optional[str] = None) -> None:
        # No model loading needed for mock
        pass

    def validate_content(self, page_data: KSAttributes, validate_params: List[ValidationOption]) -> Dict[ValidationOption, bool]:
        # Simulate a delay to mimic real model processing time
        time.sleep(2)
        # TODO: call model to compare
        import random
        result = {
            ValidationOption(id_param): bool(random.randint(0, 1))
            for id_param in validate_params
        }
        return result
