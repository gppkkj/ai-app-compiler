from pydantic import BaseModel
from typing import List

class IntentContract(BaseModel):
    app_name: str
    app_type: str
    features: List[str]
    roles: List[str]
    entities: List[str]