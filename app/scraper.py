from bs4 import BeautifulSoup
import requests
import json
from app.schemas.ks import KSAttributes
import time
from typing import List, Optional, Dict


# def fetch_and_parse(url: str) -> dict:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     title = soup.find('title').get_text()
#     content = soup.get_text()
#
#     return {"title": title, "content": content}


class ParserWeb:

    def __init__(self, urls: List[str]) -> None:
        self.urls: set = set(urls)
        self.urls_with_attributes: Dict[str, Optional[KSAttributes]] = {}

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
        for url in self.urls:
            if self.is_real_url(url):
                attr = self.get_attributes_ks(url)
                if attr:
                    self.urls_with_attributes[url] = self.get_attributes_ks(url)


def fetch_and_parse(url: str) -> dict:
    # Simulate a network delay for fetching and parsing
    # web = ParserWeb(["https://zakupki.mos.ru/auction/9869986"])
    # web.start()
    # print(web.urls_with_attributes)

    time.sleep(2)
    return {
        "title": "Mock Page Title",
        "content": "This is the mock content of the page for testing."
    }
