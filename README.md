# Agent Engineering

一个基于 Python 和大语言模型构建的模块化 Agent 系统，旨在通过工程实践学习 Agent 的核心原理与开发方法。

## 1. 项目简介

本项目从零构建一个 Agent 系统，逐步实现大语言模型调用、工具调用、上下文管理、Memory 和 RAG 等核心能力。

项目采用模块化、分层架构设计，注重代码的可维护性、可扩展性和可测试性。

## 2. 项目功能

- [x] 项目基础结构
- [x] FastAPI 服务
- [x] LLM API 调用

## 3. 项目架构

```
projects
    └─llm_service_api
```

### 模块说明

| 模块            | 职责                    |
| --------------- | ----------------------- |
| llm_service_api | HTTP 接口及请求响应模型 |
|                 |                         |
|                 |                         |
|                 |                         |
|                 |                         |
|                 |                         |

## 4. 技术栈

- Python 3.11+
- Conda
- FastAPI
- Pydantic
- DeepSeek API
- Pytest

## 5. 环境要求

- Python 3.11 或更高版本
- Conda
- Git
- DeepSeek API Key

## 6. 安装与配置

### 6.1 克隆项目

```
git clone https://github.com/你的用户名/agent-engineering.git
cd agent-engineering
```

### 6.2 创建 Conda 环境

```
conda create -n agent-engineering python=3.11
conda activate agent-engineering
```

### 6.3 安装依赖

```
pip install -e .
```

### 6.4 配置环境变量

复制环境变量模板：

```
cp .env.example .env
```

编辑 `.env`：

```
DEEPSEEK_API_KEY=your_api_key_here
MODEL_NAME=deepseek-chat
```

请勿将包含真实 API Key 的 `.env` 文件提交到 GitHub。

## 7. 运行项目

启动 FastAPI 服务：

```
uvicorn agent_engineering.main:app --reload
```

服务启动后访问：

- API 服务：http://127.0.0.1:8000
- Swagger 文档：http://127.0.0.1:8000/docs

## 8. API 使用示例

### POST /chat

请求：

```
{
    "query": "什么是 Agent？"
}
```

返回示例：

```
{
    "answer": "Agent 是一种能够感知环境、进行决策并执行任务的智能系统。"
}
```

以上接口和返回结构为示例，请以实际实现为准。

## 9. 运行测试

执行全部测试：

```
pytest -v
```

## 10. 开发计划

- 完成基础 LLM Client
- 实现 Agent 执行循环
- 实现工具注册和调用
- 实现会话管理
- 实现 Memory
- 实现 RAG
- 完善自动化测试
- 完善项目文档

## 11. 相关文档

- [项目架构设计](docs/architecture.md)
- [开发说明](docs/development.md)
- [常见问题](docs/troubleshooting.md)

## 12. License

本项目采用 MIT License。