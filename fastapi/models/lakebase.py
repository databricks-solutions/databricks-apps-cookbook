from sqlmodel import SQLModel
from typing import List


class LakebaseResourcesResponse(SQLModel):
    instance: str
    catalog: str
    synced_table: str
    message: str


class LakebaseResourcesDeleteResponse(SQLModel):
    deleted_resources: List[str]
    failed_deletions: List[str]
    message: str