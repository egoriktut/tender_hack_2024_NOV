from typing import List

from pydantic import BaseModel


class KSAttributes(BaseModel):
    files: List[dict]
    name: str
    isContractGuaranteeRequired: bool
    isLicenseProduction: bool
    deliveries: List[dict]
    startCost: float
    nextCost: float | None
