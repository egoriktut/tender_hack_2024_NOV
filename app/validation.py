import json
import re
import os
from typing import Dict, List, Optional

from celery.bin.control import status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer, util

import requests
import random

from fuzzywuzzy import fuzz
from num2words import num2words
import camelot
from transformers.utils import download_url
from transformers.utils.chat_template_utils import description_re
from websockets.asyncio.server import serve

from app.schemas.api import ValidationOption, ValidationOptionResult
from app.schemas.ks import KSAttributes
from app.utils.file_util import read_file


class KSValidator:
    def __init__(self, model_path: Optional[str] = None) -> None:
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
    ) -> Dict[ValidationOption, ValidationOptionResult]:
        validation_checks = {
            ValidationOption.VALIDATE_NAMING: self.validate_naming,
            ValidationOption.VALIDATE_PERFORM_CONTRACT_REQUIRED: self.validate_perform_contract_required,
            ValidationOption.VALIDATE_LICENSE: self.validate_license,
            ValidationOption.VALIDATE_DELIVERY_GRAPHIC: lambda: bool(
                random.randint(0, 1)
            ),
            ValidationOption.VALIDATE_PRICE: lambda: bool(random.randint(0, 1)),
            ValidationOption.VALIDATE_SPECIFICATIONS: self.validate_specifications,
        }

        for file in page_data.files:
            self.download_file(
                file["downloads_link"], file["name"], page_data.auction_id
            )
            file_path = f'./resources/_{page_data.auction_id}_{file["name"]}'
            text_pdf, text_pdf_plain, pandas_tables = read_file(file_path)
            file["decrypt"] = text_pdf
            file["decrypt_plain"] = text_pdf_plain
            file["pandas_tables"] = pandas_tables
            print("HERE")
            # try:
            #     os.remove(f"{file_path}.decrypt")
            # except FileNotFoundError:
            #     pass

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

        rubles_formatted = f"{rubles:,}".replace(",", " ")
        rubles_in_words = num2words(rubles, lang="ru").replace(" ", " ")
        kopecks_in_words = num2words(kopecks, lang="ru").replace(" ", " ")

        return f"{rubles_formatted} ({rubles_in_words}) рублей {kopecks:02d} ({kopecks_in_words}) копеек"

    def validate_perform_contract_required(self, page_data: KSAttributes) -> ValidationOptionResult:
        if isinstance(page_data.isContractGuaranteeRequired, bool):
            for file in page_data.files:
                if file["decrypt_plain"] is None:
                    continue
                text_to_check = file["decrypt_plain"].lower().strip()
                normalized_text = re.sub(r"\s+", " ", text_to_check)
                text_to_check = normalized_text.strip()
                pattern = r"размер обеспечения исполнения Контракта составляет\s+\d+(?:\s\d+)*\sрублей\s\d{2}\sкопеек".lower()
                if re.search(pattern, text_to_check):
                    return ValidationOptionResult(status=False, description="")
            return ValidationOptionResult(status=True, description="")

        else:
            for file in page_data.files:
                if file["decrypt_plain"] is None:
                    continue
                expected_text = self.number_to_words(
                    page_data.isContractGuaranteeRequired
                )
                text_to_check = file["decrypt_plain"].lower().strip()
                normalized_text = re.sub(r"\s+", " ", text_to_check)
                text_to_check = normalized_text.strip()
                # print(text_to_check)
                pattern = (
                    r"размер\s*обеспечения\s*исполнения\s*контракта\s*составляет\s*"
                    + re.escape(expected_text.lower())
                )
                # print(pattern)
                if re.search(pattern, text_to_check):
                    return ValidationOptionResult(status=True, description="")
            return ValidationOptionResult(status=False, description="")

    def validate_naming(self, page_data: KSAttributes) -> ValidationOptionResult:
        for file in page_data.files:
            if not file["decrypt_plain"] or not isinstance(file["decrypt_plain"], str):
                continue
            if not file["name"].endswith(".doc") and not file["name"].endswith(".docx"):
                continue
            file_txt = file["decrypt_plain"]
            normalized_text = re.sub(r'[^a-zA-Zа-яА-Я0-9.,;:"\'\s-]', "", file_txt)
            normalized_text = re.sub(r"\s+", " ", normalized_text)
            normalized_text = normalized_text.strip()

            target_phrase_start = "ТЕХНИЧЕСКОЕ ЗАДАНИЕ"
            match_start = re.search(target_phrase_start, normalized_text[:250], re.IGNORECASE)
            start_index = 0
            if match_start:
                start_index = match_start.start() + len(target_phrase_start)

            target_phrase_end = "Общая информация об объекте закупки"
            match_end = re.search(target_phrase_end, normalized_text[:250], re.IGNORECASE)
            end_index = start_index + len(page_data.name) + 100
            if match_end:
                end_index = match_end.start()

            print(f"START {start_index}, END {end_index}")
            similarity_score = fuzz.partial_ratio(
                page_data.name.lower(), normalized_text[start_index:end_index].lower()
            )
            print(
                f"LOLOLOL OMAGAD EEGORIK {similarity_score}, start {start_index} end {end_index}, name {page_data.name} ||| - text {normalized_text[start_index:end_index]}"
            )
            if similarity_score > 70:
                return ValidationOptionResult(status=True, description=f"{similarity_score}%")
            print("CHECE", normalized_text[:200])

            tf1_score = self.check_similarity_transformer(page_data.name, normalized_text[start_index:end_index])
            if tf1_score >= 0.75:
                return ValidationOptionResult(status=True, description=f"{tf1_score:.1%}")

            tf2_score = self.check_similarity2_transformer(page_data.name, normalized_text[start_index:end_index])
            if tf2_score < 5:
                return ValidationOptionResult(status=True, description=f"{tf2_score:.1%}")

        return ValidationOptionResult(status=False, description="не найдено")

    def check_similarity_transformer(self, name: str, text: str) -> int:
        interface_name = name
        td_name = text

        # Преобразование текстов в векторы
        interface_embedding = self.model.encode(interface_name, convert_to_tensor=True)
        td_embedding = self.model.encode(td_name, convert_to_tensor=True)

        # Вычисление сходства
        similarity_score = util.cos_sim(interface_embedding, td_embedding).item()
        print(f"TRANFORMER OPTIMUS {similarity_score}, name {name}, text {text}")

        return similarity_score

    def check_similarity2_transformer(self, name: str, text: str) -> int:
        # Тексты для проверки
        interface_name = name
        td_name = text

        # Получение векторов
        interface_embedding = self.model.encode(interface_name)
        td_embedding = self.model.encode(td_name)

        # Евклидово расстояние между векторами
        euclidean_distance = np.linalg.norm(interface_embedding - td_embedding)
        print(f"TRANFORMER BUMBELBIE {euclidean_distance}, name {name}, text {text}")
        return euclidean_distance

    def validate_specifications(self, api_data: KSAttributes) -> ValidationOptionResult:
        validation_checks = []
        for file in api_data.files:
            if not (
                "тз" in file["name"].lower()
                or "техническое" in file["name"].lower() and "задание" in file["name"].lower()
            ):
                return ValidationOptionResult(status=False, description="нет ТЗ")
            reference_col_name = {
                "name": ["Наименование", "Название"],
                "quantity": ["Кол.", "Кол-", "Кол-во", "Количество"],
                "date": ["сроки", "срок", "Дата"],
                "cost": ["Стоимость", "Цена", "Стоим"],
            }
            deliveries = api_data.deliveries
            from collections import defaultdict

            aggregated_items = defaultdict(lambda: {"sum": 0.0, "quantity": 0.0, "costPerUnit": 0.0, "name": ""})

            for delivery in deliveries:
                for item in delivery.get("items", []):
                    name = item["name"]

                    aggregated_items[name]["name"] = name
                    aggregated_items[name]["sum"] += item["sum"]
                    aggregated_items[name]["quantity"] += item["quantity"]
                    aggregated_items[name]["costPerUnit"] = item["costPerUnit"]
            print("AGGREEGATED")
            print(aggregated_items)
            unique_items = list(aggregated_items.values())


            for item in unique_items:
                print(item)

            tables = file["pandas_tables"]
            validated_items: List = []
            if tables is None:
                continue
            for table in tables:
                col_name_mapper: dict = self.map_pdf_columns(reference_col_name, table.df.iloc[0])
                print(col_name_mapper)
                for idx, res_row in enumerate(unique_items):
                    # dont touch header row

                    for index, row in table.df[1:].iterrows():
                        # try for invalid tables
                        try:
                            print(row)
                            name = row.get(col_name_mapper['name'], None)
                            quantity = row.get(col_name_mapper.get('quantity', None), None)
                            cost = row.get(col_name_mapper.get('cost', None), None)
                            date = row.get(col_name_mapper.get('date', None), None)
                            print(self.check_similarity_transformer(name, res_row['name']), self.checkSpecDate(date, res_row["periodDaysTo"]), self.checkSpecCost(cost, res_row[cost]), self.checkSpecEquantity(quantity, res_row['quantity']))
                            if self.check_similarity_transformer(name, res_row['name']) and self.checkSpecDate(date, res_row["periodDaysTo"]) and self.checkSpecCost(cost, res_row[cost]) and self.checkSpecEquantity(quantity, res_row['quantity']):
                                validated_items.append(res_row)
                        
                        except:
                            print("err")
                            break
            print(len(validated_items))
            print(len(unique_items))
            validation_checks.append(len(validated_items) == len(unique_items))
        print(validation_checks)

        return ValidationOptionResult(status=all(validation_checks), description="")

    def checkSpecDate(self, pdf_date: str, api_date: str) -> bool:
        if pdf_date is None or api_date is None:
            return False
        return api_date in pdf_date

    def checkSpecCost(self, pdf_cost: str, api_cost: str) -> bool:
        if pdf_cost is None or api_cost is None:
            return False
        return pdf_cost == api_cost
    
    def checkSpecEquantity(self, pdf_eq: str, api_eq: str) -> bool:
        if pdf_eq is None or api_eq is None:
            return False
        return pdf_eq == api_eq

    # map columns name to col id
    @staticmethod
    def map_pdf_columns(column_name_map, pdf_columns):
        mapped_columns = {}
        for std_name, alternatives in column_name_map.items():
            found_mapping = False
            i = 0
            for pdf_col in pdf_columns:
                if found_mapping:
                    break
                for alt in alternatives:
                    if alt.lower() in pdf_col.lower():
                        mapped_columns[std_name] = i
                        found_mapping = True
                i += 1


        return mapped_columns

    @staticmethod
    def check_specification_name_equality(pdf_text: str, api_text: str) -> bool:
        similarity_score = fuzz.partial_ratio(
            pdf_text.lower(), api_text.lower()
        )
        inversed_similarity_score = fuzz.partial_ratio(
            pdf_text.lower(), api_text.lower()
        )
        print(pdf_text, api_text, "similarity", similarity_score, inversed_similarity_score)
        return similarity_score > 80 or inversed_similarity_score > 80

    def validate_license(self, page_data: KSAttributes):
        license_text = page_data.isLicenseProduction
        print(license_text)
        if isinstance(license_text, bool):
            for file in page_data.files:
                if file["decrypt_plain"] is None:
                    continue
                text_to_check = file["decrypt_plain"].lower().strip()
                normalized_text = re.sub(r"\s+", " ", text_to_check)
                text_to_check = normalized_text.strip()
                pattern1 = r"\s*лицензи\s*"
                pattern2 = r"\s*сертификат\s*"
                if re.search(pattern1, text_to_check) and re.search(pattern2, text_to_check):
                    ValidationOptionResult(status=False, description="найдены совпадения")
            return ValidationOptionResult(status=True, description="не найдено")

        else:
            max_similarity = 0
            for file in page_data.files:
                if file["decrypt_plain"] is None:
                    continue
                text_to_check = file["decrypt_plain"].lower().strip()
                normalized_text = re.sub(r"\s+", " ", text_to_check)
                text_to_check = normalized_text.strip()
                licenses_indices = [i.start() for i in re.finditer("лицензи", text_to_check)]
                certificate_indices = [i.start() for i in re.finditer("сертификат", text_to_check)]
                for index in licenses_indices + certificate_indices:
                    start_index = max(0, index - 5)
                    end_index = min(len(text_to_check), index + len(license_text) - 5)
                    substring = normalized_text[start_index:end_index]
                    similarity_score = fuzz.partial_ratio(license_text.lower(), substring.lower())
                    max_similarity = max(max_similarity, similarity_score)
                    if similarity_score > 80:
                        return ValidationOptionResult(status=True, description=f"{max_similarity}%")
            return ValidationOptionResult(status=False, description=f"{max_similarity}%")
