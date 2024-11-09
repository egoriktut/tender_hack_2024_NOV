import json
from typing import Optional

import requests

from app.schemas.ks import KSAttributes


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
                auction_id=auction_id,
                files=[
                    {
                        "name": file["name"],
                        "downloads_link": f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file['id']}",
                    }
                    for file in result["files"]
                ],
                name=result["name"],
                isContractGuaranteeRequired=(
                    result["contractGuaranteeAmount"]
                    if result["isContractGuaranteeRequired"]
                    else False
                ),
                isLicenseProduction=(
                    result["uploadLicenseDocumentsComment"]
                    if result["isLicenseProduction"]
                    else False
                ),
                deliveries=result["deliveries"],
                startCost=result["startCost"],
                contractCost=result["contractCost"],
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
