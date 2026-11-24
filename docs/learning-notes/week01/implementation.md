# 自己实现的功能和代码

实现[fastapi调用deepseek](../../../projects/llm_service_api/app/chat.py)

该模块通过定义`ChatRequest`和`ChatResponse`两个pydantic模型规范了/chat接口的输入与输出

这两个模型的设计需要遵循

| 设计对象       | 主要参考依据              | 核心问题                     |
| -------------- | ------------------------- | ---------------------------- |
| ChatRequest    | DeepSeek API + 客户端需求 | 用户需要提交什么？           |
| ChatMessage    | DeepSeek 消息格式         | 一条对话消息包含什么？       |
| ChatResponse   | FastAPI 服务设计          | 用户需要获得什么？           |
| Field          | 参数约束需求              | 什么样的数据是合法的？       |
| response_model | FastAPI 响应规范          | 返回的数据应该符合什么结构？ |

同时要注意请求和响应并不需要和DeepSeekAPI给出的**数据结构完全一致**

流式输出每次获取的是增量的内容可能每次只有一个词或短句，fastapi为流式输出提供了标准格式SSE