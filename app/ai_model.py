# import json
# from typing import Dict, List, Optional
#
# import requests
# from celery.bin.result import result
#
# from app.schemas.api import ValidationOption
# from app.schemas.ks import KSAttributes
# from app.utils.file_util import read_file
#
#
# class ModelInference:
#     def __init__(self, model_path: Optional[str] = None) -> None:
#         # No model loading needed for mock
#         pass
#
#     @staticmethod
#     def download_file(download_link: str, file_name: str, auction_id: int) -> None:
#         response = requests.get(download_link, stream=True)
#         response.raise_for_status()
#         import os
#
#         os.makedirs("resources", exist_ok=True)
#
#         file_path = f"./resources/_{auction_id}_{file_name}"
#         with open(file_path, "wb") as file:
#             for chunk in response.iter_content(chunk_size=8192):
#                 if chunk:
#                     file.write(chunk)
#
#     def validate_content(
#         self, page_data: KSAttributes, validate_params: List[ValidationOption]
#     ) -> Dict[ValidationOption, bool]:
#         # TODO: call model to compare
#         import os
#
#         for file in page_data.files:
#             self.download_file(file["downloads_link"], file["name"], page_data.auction_id)
#             file_path = f'./resources/_{page_data.auction_id}_{file["name"]}'
#             file["decrypt"] = read_file(file_path)
#             os.remove(file_path)
#             try:
#                 os.remove(f"{file_path}.decrypt")
#             except FileNotFoundError:
#                 pass
#
#         output_file_path = f"./resources/{page_data.auction_id}_result.json"
#         with open(output_file_path, "a+", encoding="utf-8") as f:
#             f.write(json.dumps(page_data.json(), ensure_ascii=False, indent=4))
#
#         import random
#
#         result = {
#             ValidationOption(id_param): bool(random.randint(0, 1))
#             for id_param in validate_params
#         }
#         return result
