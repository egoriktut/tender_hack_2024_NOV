import time
from typing import Dict, Any, Optional


class ModelInference:
    def __init__(self, model_path: Optional[str] = None) -> None:
        # No model loading needed for mock
        pass

    def validate_content(self, content: str) -> Dict[str, Any]:
        # Simulate a delay to mimic real model processing time
        time.sleep(2)
        return {"mock_analysis": "This content appears valid and well-structured."}
