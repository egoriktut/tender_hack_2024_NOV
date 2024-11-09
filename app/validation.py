import json
import re
import os
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer, util

import requests
import random

from fuzzywuzzy import fuzz
from num2words import num2words
import camelot

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
            ValidationOption.VALIDATE_SPECIFICATIONS: self.validate_specifications,
        }

        for file in page_data.files:
            self.download_file(
                file["downloads_link"], file["name"], page_data.auction_id
            )
            file_path = f'./resources/_{page_data.auction_id}_{file["name"]}'
            text_pdf, text_pdf_plain = read_file(file_path)
            file["decrypt"] = text_pdf
            file["decrypt_plain"] = text_pdf_plain
            print("HERE")
            try:
                os.remove(f"{file_path}.decrypt")
            except FileNotFoundError:
                pass

        output_file_path = f"./resources/{page_data.auction_id}_result.json"
        with open(output_file_path, "a+", encoding="utf-8") as f:
            f.write(json.dumps(page_data.json(), ensure_ascii=False, indent=4))

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

    def validate_perform_contract_required(self, page_data: KSAttributes) -> bool:
        if isinstance(page_data.isContractGuaranteeRequired, bool):
            for file in page_data.files:
                if file["decrypt_plain"] is None:
                    continue
                text_to_check = file["decrypt_plain"].lower().strip()
                normalized_text = re.sub(r"\s+", " ", text_to_check)
                text_to_check = normalized_text.strip()
                pattern = r"размер обеспечения исполнения Контракта составляет\s+\d+(?:\s\d+)*\sрублей\s\d{2}\sкопеек".lower()
                if re.search(pattern, text_to_check):
                    return False
            return True

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
                    return True
            return False

    def validate_naming(self, page_data: KSAttributes) -> bool:
        for file in page_data.files:
            if not file["decrypt_plain"] or not isinstance(file["decrypt_plain"], str):
                continue
            if not file["name"].endswith(".doc") and not file["name"].endswith(".docx"):
                continue
            file_txt = file["decrypt_plain"]
            normalized_text = re.sub(r'[^a-zA-Zа-яА-Я0-9.,;:"\'\s-]', "", file_txt)
            normalized_text = re.sub(r"\s+", " ", normalized_text)
            normalized_text = normalized_text.strip()

            target_phrase = "ТЕХНИЧЕСКОЕ ЗАДАНИЕ"
            match = re.search(target_phrase, normalized_text[:250], re.IGNORECASE)
            start_index = 0
            if match:
                start_index = match.start() + len(target_phrase)
            print(f"START INDEX {start_index}")
            for end in range(len(page_data.name)+40, len(page_data.name) + 140, 10):
                similarity_score = fuzz.partial_ratio(
                    page_data.name.lower(), normalized_text[start_index:end].lower()
                )
                print(
                    f"LOLOLOL OMAGAD EEGORIK {similarity_score}, start {start_index} end {end}, name {page_data.name} ||| START {start_index} - text {normalized_text[start_index:end]}"
                )
                if similarity_score > 70:
                    return True
            print("CHECE", normalized_text[:100])
            tf_result = self.check_similarity_transformer(page_data.name, normalized_text[start_index:start_index+200])
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

    def validate_specifications(self, api_data: KSAttributes):
        validation_checks = []
        for file in api_data.files:
            reference_col_name = {
                "name": ["Наименование", "Название"],
                "quantity": ["Кол.", "Кол-", "Кол-во", "Количество"],
                "date": ["сроки", "срок", "Дата"],
                # "cost": ["Стоимость", "Цена", "Стоим."],
            }

            items = api_data.deliveries['items']
            items_map = {}

            for item_list in items:
                for item in item_list:
                    if item['name'] in items_map:
                        items_map[item['name']]['quantity'] += item['quantity']
                        items_map[item['name']]['sum'] += item['sum']
                    else:
                        items_map[item['name']] = item
            items = []
            for key, value in items_map:
                items.append(value)
            print("ITEMS: ", items)

            tables = file["tables"]
            validated_items: List = []

            for table in tables:
                col_name_mapper: dict = self.map_pdf_columns(reference_col_name, table.df.iloc[0])

                for idx, res_row in enumerate(items):
                    # dont touch header row
                    for index, row in table.df[1:].iterrows():
                        # try for invalid tables
                        try:
                            name = row[col_name_mapper['name']]
                            quantity = row[col_name_mapper.get('quantity', None)]
                            date = row[col_name_mapper.get('date', None)]
                            if (self.check_specification_name_equality(name, res_row['name'])
                                and res_row['periodDaysTo'] in date
                                and quantity == res_row['quantity']):
                                validated_items.append(res_row)
                        except:
                            print("err")
                            break
            validation_checks.append(len(validated_items) == len(items))
        return all(validation_checks)



    # map columns name to col id
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
    
    def check_specification_name_equality(pdf_text: str, api_text: str) -> bool:
        similarity_score = fuzz.partial_ratio(
            pdf_text.lower(), api_text.lower()
        )
        inversed_similarity_score = fuzz.partial_ratio(
            pdf_text.lower(), api_text.lower()
        )
        print(pdf_text, api_text, "similarity", similarity_score, inversed_similarity_score)
        return similarity_score > 80 or inversed_similarity_score > 80
