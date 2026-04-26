from pydantic import BaseModel, Field
from typing import List, Optional, Union


class FileData(BaseModel):
    uri: Optional[str] = None
    bytes: Optional[str] = None
    mime_type: str


class PartModel(BaseModel):
    text: Optional[str] = None
    file: Optional[FileData] = None


class MessageModel(BaseModel):
    role: str = Field(..., example="user")
    parts: List[PartModel]


class A2ARequestModel(BaseModel):
    message: MessageModel
    context_id: Optional[str] = None
    task_id: Optional[str] = None
