from typing import List

from pydantic import BaseModel


class KSAttributes(BaseModel):
    files: List[dict]
    auction_id: int
    name: str
    isContractGuaranteeRequired: float | bool
    isLicenseProduction: str | bool
    deliveries: List[dict]
    startCost: float
    contractCost: float | None
