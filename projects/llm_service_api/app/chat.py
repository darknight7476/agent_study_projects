from fastapi.responses import StreamingResponse
from .model import ChatResponse, ChatRequest
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import json
import os

def generate_stram()


# 1.初始化fastapi
app = FastAPI()

# 2.初始化deepseek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    timeout=60
)

# 3. 实现聊天接口
@app.post('/chat', response_model=ChatResponse)
def deepseek_chat(messages: ChatRequest):
    try:
        response = client.chat.completions.create(
            model=messages.model,
            messages=[msg.model_dump() for msg in messages.messages],
            stream=messages.stream,
            max_tokens=messages.max_tokens,
            temperature=messages.temperature,
            extra_body={'thinking': messages.thinking},
        )
        content = response.choices[0].message
        return ChatResponse(
            role=content.role,
            model=response.model,
            content=content.content,
            usage_token=response.usage.total_tokens
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模型调用失败：{str(e)}"
        )

@app.post('/chat/stram')
def deepseek_chat_stram(messages: ChatRequest):
