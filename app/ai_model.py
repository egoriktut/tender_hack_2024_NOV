import time
from typing import Any, Dict, List, Optional

import requests

from app.schemas.api import ValidationOption
from app.schemas.ks import KSAttributes
from app.utils.file_util import read_file


class ModelInference:
    def __init__(self, model_path: Optional[str] = None) -> None:
        # No model loading needed for mock
        pass

    @staticmethod
    def download_file(download_link: str, file_name: str) -> None:
        response = requests.get(download_link, stream=True)
        response.raise_for_status()
        import os

        os.makedirs("resources", exist_ok=True)

        file_path = f"./resources/{file_name}"
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    def validate_content(
        self, page_data: KSAttributes, validate_params: List[ValidationOption]
    ) -> Dict[ValidationOption, bool]:
        # time.sleep(2)
        # TODO: call model to compare
        for file in page_data.files:
            self.download_file(file["downloads_link"], file["name"])
            file["decrypt"] = read_file(f'./resources/{file["name"]}')

        print(page_data)

        import random

        result = {
            ValidationOption(id_param): bool(random.randint(0, 1))
            for id_param in validate_params
        }
        return result
