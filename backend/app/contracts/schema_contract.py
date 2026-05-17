from pydantic import BaseModel
from typing import List, Dict


class DatabaseTable(BaseModel):
    name: str
    fields: Dict[str, str]


class ApiEndpoint(BaseModel):
    path: str
    method: str


class UiPage(BaseModel):
    name: str
    components: List[str]


class AuthRule(BaseModel):
    role: str
    permissions: List[str]


class SchemaContract(BaseModel):

    database: List[DatabaseTable]

    api: List[ApiEndpoint]

    ui: List[UiPage]

    auth: List[AuthRule]