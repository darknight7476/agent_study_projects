# 问题、错误和解决方案

## 问题1

**现象**：调用流式接口时不返回内容只会返回最后的`[DONE]`

**原因**：在编写流式接口时没有注意` if not chunk.choices:`写成` if chunk.choices:`导致所有流式输出全被跳过

**正确现象**：SSE输出

```
event: message
data: {"model": "deepseek-flash", "content": "\u4f60\u597d", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\uff01", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\u6709\u4ec0\u4e48", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\u6211\u53ef\u4ee5", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\u5e2e", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\u4f60\u7684", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\u5417", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\uff1f", "usage_token": null}

event: message
data: {"model": "deepseek-flash", "content": "\ud83d\ude0a", "usage_token": null}

event: done
data: [DONE]
```
