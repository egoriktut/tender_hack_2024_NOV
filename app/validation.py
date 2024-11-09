import re
import os
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer, util

import requests
import random

from fuzzywuzzy import fuzz
from num2words import num2words

from app.schemas.api import ValidationOption
from app.schemas.ks import KSAttributes
from app.utils.file_util import read_file


class KSValidator:
    def __init__(self, model_path: Optional[str] = None) -> None:
        # No model loading needed for mock
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    @staticmethod
    def download_file(download_link: str, file_name: str, auction_id: int) -> None:
        response = requests.get(download_link, stream=True)
        response.raise_for_status()

        os.makedirs("resources", exist_ok=True)

        file_path = f"./resources/_{auction_id}_{file_name}"
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    def validate_content(
        self, page_data: KSAttributes, validate_params: List[ValidationOption]
    ) -> Dict[ValidationOption, bool]:
        validation_checks = {
            ValidationOption.VALIDATE_NAMING: self.validate_naming,
            ValidationOption.VALIDATE_PERFORM_CONTRACT_REQUIRED: self.validate_perform_contract_required,
            ValidationOption.VALIDATE_LICENSE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_DELIVERY_GRAPHIC: lambda: bool(
                random.randint(0, 1)
            ),
            ValidationOption.VALIDATE_PRICE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_SPECIFICATIONS: lambda: bool(
                random.randint(0, 1)
            ),
        }

        for file in page_data.files:
            self.download_file(
                file["downloads_link"], file["name"], page_data.auction_id
            )
            file_path = f'./resources/_{page_data.auction_id}_{file["name"]}'
            text_pdf = read_file(file_path)
            if text_pdf:
                normalized_text = re.sub(r'[^a-zA-Zа-яА-Я0-9.,;:"\'\s-]', "", text_pdf)
                normalized_text = re.sub(r"\s+", " ", normalized_text)
                text_pdf = normalized_text.strip()
            file["decrypt"] = text_pdf
            os.remove(file_path)
            try:
                os.remove(f"{file_path}.decrypt")
            except FileNotFoundError:
                pass

        # output_file_path = f"./resources/{page_data.auction_id}_result.json"
        # with open(output_file_path, "a+", encoding="utf-8") as f:
        #     f.write(json.dumps(page_data.json(), ensure_ascii=False, indent=4))

        validation_result = {
            option: validation_checks[option](page_data)
            for option in validate_params
            if option in validation_checks
        }

        return validation_result

    @staticmethod
    def number_to_words(number: float) -> str:
        rubles = int(number)
        kopecks = int((number - rubles) * 100)

        rubles_in_words = num2words(rubles, lang="ru").replace(" ", " ")
        kopecks_in_words = num2words(kopecks, lang="ru").replace(" ", " ")

        return f"{rubles} ({rubles_in_words}) рублей {kopecks:02d} ({kopecks_in_words}) копеек"

    def validate_perform_contract_required(self, page_data: KSAttributes) -> bool:
        if isinstance(page_data.isContractGuaranteeRequired, bool):
            for file in page_data.files:
                text_to_check = file["decrypt"]
                pattern = r"Размер обеспечения исполнения Контракта составляет\s+\d+(?:\s\d+)*\sрублей\s\d{2}\sкопеек".lower()
                if re.search(pattern, text_to_check):
                    return False
                return True

        else:
            for file in page_data.files:
                expected_text = self.number_to_words(
                    page_data.isContractGuaranteeRequired
                )
                text_to_check = file["decrypt"].lower()
                pattern = re.escape(
                    f"Размер обеспечения исполнения Контракта составляет {expected_text}".lower()
                )
                if re.search(pattern, text_to_check):
                    return True
                return False

    def validate_naming(self, page_data: KSAttributes) -> bool:
        for file in page_data.files:
            if not file["decrypt"] or not isinstance(file["decrypt"], str):
                continue
            file_txt = file["decrypt"]

            window = len(page_data.name) + 40
            for start in range(0, min(200, len(str(file_txt))), 10):
                end = min(start + window, len(file_txt) - 1)
                similarity_score = fuzz.partial_ratio(
                    page_data.name.lower(), file_txt[start:end].lower()
                )
                print(
                    f"LOLOLOL OMAGAD EEGORIK {similarity_score}, start {start} end {end}, name {page_data.name} ||| text {file_txt[start:end]}"
                )
                if similarity_score > 70:
                    return True

            tf_result = self.check_similarity_transformer(page_data.name, file_txt[:50])
            if tf_result:
                return True

        return False

    def check_similarity_transformer(self, name: str, text: str) -> bool:
        interface_name = name
        td_name = text

        # Преобразование текстов в векторы
        interface_embedding = self.model.encode(interface_name, convert_to_tensor=True)
        td_embedding = self.model.encode(td_name, convert_to_tensor=True)

        # Вычисление сходства
        similarity_score = util.cos_sim(interface_embedding, td_embedding).item()
        print(f"TRANFORMER OPTIMUS {similarity_score}, name {name}, text {text}")

        # Установка порогового значения
        threshold = 0.75
        # Вывод результата
        if similarity_score >= threshold:
            return True
        else:
            return False
