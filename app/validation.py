import re
from typing import Dict, List, Optional

import requests
import random

from app.schemas.api import ValidationOption
from app.schemas.ks import KSAttributes
from app.utils.file_util import read_file


class KSValidator:
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
        validation_checks = {
            ValidationOption.VALIDATE_NAMING: self.validate_naming,
            ValidationOption.VALIDATE_PERFORM_CONTRACT_REQUIRED: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_LICENSE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_DELIVERY_GRAPHIC: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_PRICE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_SPECIFICATIONS: lambda: bool(random.randint(0, 1))

        }

        for file in page_data.files:
            self.download_file(file["downloads_link"], file["name"])
            file["decrypt"] = read_file(f'./resources/{file["name"]}')


        validation_result = {
            option: validation_checks[option](page_data) for option in validate_params if option in validation_checks
        }

        return validation_result

    def validate_naming(self, page_data: KSAttributes) -> bool:
        for file in page_data.files:
            if not file["decrypt"] or not isinstance(file["decrypt"], str):
                continue
            file_txt = file["decrypt"]
            # print(file_txt)
            normalized_text = re.sub(r'[^a-zA-Zа-яА-Я0-9.,;:"\'\s-]', '', file_txt)
            normalized_text = re.sub(r'\s+', ' ', normalized_text)
            normalized_text = normalized_text.strip()

            # Output the normalized text
            print(normalized_text)
            with open("check.txt", "w", encoding="utf-8") as f:
                f.write(normalized_text)

            if page_data.name in normalized_text:
                return True
        return False
