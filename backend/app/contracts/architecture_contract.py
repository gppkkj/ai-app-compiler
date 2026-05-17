from pydantic import BaseModel
from typing import List, Dict


class FrontendConfig(BaseModel):
    pages: List[str]
    components: List[str]


class BackendConfig(BaseModel):
    services: List[str]
    endpoints: List[str]


class DatabaseConfig(BaseModel):
    tables: List[str]


class AuthConfig(BaseModel):
    roles: List[str]
    permissions: Dict[str, List[str]]


class ArchitectureContract(BaseModel):
    frontend: FrontendConfig
    backend: BackendConfig
    database: DatabaseConfig
    auth: AuthConfig