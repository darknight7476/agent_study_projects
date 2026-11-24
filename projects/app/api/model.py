from pydantic import BaseModel, Field
from typing import Literal


# 请求和响应模型实现
class ChatMessage(BaseModel):
    role: Literal['user', 'system', 'assistant']
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    max_tokens: int = Field(default=1024, gt=0)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    thinking: dict = Field(default={'type': 'disabled'})


class ChatResponse(BaseModel):
    model: str
    content: str
    usage_token: int | None = None
