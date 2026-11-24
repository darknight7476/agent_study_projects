from fastapi.sse import EventSourceResponse, ServerSentEvent
from .model import ChatResponse, ChatRequest
from fastapi import FastAPI, HTTPException
from collections.abc import AsyncIterable
from openai import AsyncOpenAI
import os

# 1.初始化fastapi
app = FastAPI()

# 2.初始化deepseek
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    timeout=60
)


# 3. 实现聊天接口
@app.post('/chat', response_model=ChatResponse)
async def deepseek_chat(messages: ChatRequest):
    try:
        response = await client.chat.completions.create(
            model=messages.model,
            messages=[msg.model_dump() for msg in messages.messages],
            stream=False,
            max_tokens=messages.max_tokens,
            temperature=messages.temperature,
            extra_body={'thinking': messages.thinking},
        )
        content = response.choices[0].message
        return ChatResponse(
            model=response.model,
            content=content.content,
            usage_token=response.usage.total_tokens
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模型调用失败：{str(e)}"
        )


@app.post('/chat/stream', response_class=EventSourceResponse)
async def deepseek_chat_stram(messages: ChatRequest) -> AsyncIterable[ServerSentEvent]:
    stream = None
    try:
        stream = await client.chat.completions.create(
            model=messages.model,
            messages=[msg.model_dump() for msg in messages.messages],
            stream=True,
            max_tokens=messages.max_tokens,
            temperature=messages.temperature,
            extra_body={'thinking': messages.thinking},
        )
        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                result = ChatResponse(
                    model=chunk.model,
                    content=content
                )
                yield ServerSentEvent(
                    data=result.model_dump(),
                    event="message"
                )
        yield ServerSentEvent(
            raw_data="[DONE]",
            event='done'
        )
    except Exception as e:
        yield ServerSentEvent(
            data={"message": "模型调用失败" + str(e)},
            event="error"
        )

    finally:
        if stream is not None:
            await stream.close()
