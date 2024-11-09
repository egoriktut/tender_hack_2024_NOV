import json
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from app.schemas.ks import KSAttributes

# def fetch_and_parse(url: str) -> dict:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     title = soup.find('title').get_text()
#     content = soup.get_text()
#
#     return {"title": title, "content": content}


class ParserWeb:

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.attributes: Optional[KSAttributes] = None

    @staticmethod
    def is_real_url(url: str) -> bool:
        result = requests.get(url)
        return result.status_code == 200

    @staticmethod
    def get_attributes_ks(url: str) -> Optional[KSAttributes]:
        try:
            auction_id = url.split("/")[-1]
            result = json.loads(
                requests.get(
                    f"https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId={auction_id}"
                ).content.decode()
            )
            result = KSAttributes(
                files=[
                    {
                        "name": file["name"],
                        "downloads_link": f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file['id']}",
                    }
                    for file in result["files"]
                ],
                name=result["name"],
                isContractGuaranteeRequired=result["isContractGuaranteeRequired"],
                isLicenseProduction=result["isLicenseProduction"],
                deliveries=result["deliveries"],
                startCost=result["startCost"],
                nextCost=result["nextCost"],
            )
            return result
        except Exception as e:
            return None

    def start(self) -> None:
        if self.is_real_url(self.url):
            attr = self.get_attributes_ks(self.url)
            if attr:
                self.attributes = self.get_attributes_ks(self.url)


def fetch_and_parse(url: str) -> Optional[KSAttributes]:
    parser = ParserWeb(url)
    attributes = parser.get_attributes_ks(url)
    return attributes
