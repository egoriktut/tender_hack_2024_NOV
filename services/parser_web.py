import json

import requests

from models.ks import KSAttributes


class ParserWeb:

    def __init__(self, urls):
        self.urls = set(urls)
        self.urls_with_attributes = {}

    @staticmethod
    def is_real_url(url):
        result = requests.get(url)
        return result.status_code == 200

    @staticmethod
    def get_attributes_ks(url):
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

    def start(self):
        for url in self.urls:
            if self.is_real_url(url):
                attr = self.get_attributes_ks(url)
                if attr:
                    self.urls_with_attributes[url] = self.get_attributes_ks(url)


web = ParserWeb(["https://zakupki.mos.ru/auction/9869986"])
web.start()
print(web.urls_with_attributes)
