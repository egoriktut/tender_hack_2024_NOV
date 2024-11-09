import re
import os
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer, util

import requests
import random

from fuzzywuzzy import fuzz

from app.schemas.api import ValidationOption
from app.schemas.ks import KSAttributes
from app.utils.file_util import read_file


class KSValidator:
    def __init__(self, model_path: Optional[str] = None) -> None:
        # No model loading needed for mock
        pass

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
            ValidationOption.VALIDATE_PERFORM_CONTRACT_REQUIRED: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_LICENSE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_DELIVERY_GRAPHIC: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_PRICE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_SPECIFICATIONS: lambda: bool(random.randint(0, 1))

        }

        for file in page_data.files:
            self.download_file(file["downloads_link"], file["name"], page_data.auction_id)
            file_path = f'./resources/_{page_data.auction_id}_{file["name"]}'
            file["decrypt"] = read_file(file_path)
            os.remove(file_path)
            try:
                os.remove(f"{file_path}.decrypt")
            except FileNotFoundError:
                pass

        # output_file_path = f"./resources/{page_data.auction_id}_result.json"
        # with open(output_file_path, "a+", encoding="utf-8") as f:
        #     f.write(json.dumps(page_data.json(), ensure_ascii=False, indent=4))

        validation_result = {
            option: validation_checks[option](page_data) for option in validate_params if option in validation_checks
        }

        return validation_result

    def validate_naming(self, page_data: KSAttributes) -> bool:
        for file in page_data.files:
            if not file["decrypt"] or not isinstance(file["decrypt"], str):
                continue
            file_txt = file["decrypt"]
            normalized_text = re.sub(r'[^a-zA-Zа-яА-Я0-9.,;:"\'\s-]', '', file_txt)
            normalized_text = re.sub(r'\s+', ' ', normalized_text)
            normalized_text = normalized_text.strip()

            window = len(page_data.name) + 40
            print("is ok")
            for start in range(min(200, len(normalized_text)), 10):
                end = min(start + window, len(normalized_text) - 1)
                similarity_score = fuzz.partial_ratio(page_data.name.lower(), normalized_text[start:end].lower())
                print(f"LOLOLOL OMAGAD EEGORIK {similarity_score}, start {start} end {end}, name {page_data.name}")
                if similarity_score > 70:
                    return True

        return False
from sentence_transformers import SentenceTransformer, util

interface_name = "ОБСЛУЖИВАНИЕ ТЕХНИЧЕСКОЕ И ТЕКУЩИЙ РЕМОНТ ЛЕГКОВЫХ АВТОМОБИЛЕЙ"
td_name = "Техническое обслуживание и текущий ремонт легковых автомобилей"

# Загрузка модели Sentence Transformers
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Преобразование текстов в векторы
interface_embedding = model.encode(interface_name, convert_to_tensor=True)
td_embedding = model.encode(td_name, convert_to_tensor=True)

# Вычисление сходства
similarity_score = util.cos_sim(interface_embedding, td_embedding).item()

# Установка порогового значения
threshold = 0.75

print(similarity_score)
# Вывод результата
if similarity_score >= threshold:
    print("Наименование закупки валидно: тексты по смыслу сопоставимы.")
else:
    print("Наименование закупки не валидно: тексты по смыслу не сопоставимы.")
