# 本周理论知识

## 类型提示

在编写python函数的时候，在设定参数的时候使用``: + 类型``，编辑器能够根据类型给出补全信息，同时还能提供错误检查，除了常用的类型还能使用``typing模块``扩充

```python
def some_function(data: str):
```

类似可以使用``list[str]``,声明内部值类型的类型称为**泛型类型**

```python
def process_items(items: list[str]):
def process_items(items_t: tuple[int, int, str], items_s: set[bytes]):
def process_items(prices: dict[str, float]):
```

如果取值类型是多个里面选一个可以使用联合类型定义

```python
def process_item(item: int | str):
```

还接收使用自定义类去给定类型，此时认定为实例

pydantic库支持将数据的结构按照类的属性进行定义

```python
class User(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: datetime | None = None
    friends: list[int] = []
```

``Annotated``支持在类型提示中加入额外的**元数据**

```python
def say_hello(name: Annotated[str, "this is just metadata"]) -> str:
```

## 并发与异步

在项目运行过程中，不可避免的程序需要进行相对较慢**I/O密集型**操作，如果按照**同步**顺序执行流程，那么不可避免的会出现计算机等待的空白时间段，为了重复利用计算机性能采用与慢任务“**异步**”，让计算机先去完成其它任务，等执行完毕后，再检查异步任务队列是否存在已经完成的任务继续处理。

>I/O密集型如：
>
>- 通过网络发送来自客户端的数据
>- 客户端通过网络接收由你的程序发送的数据
>- 磁盘中文件的内容被系统读取并提供给你的程序
>- 你的程序提供给系统的内容被写入磁盘
>- 一个 API 的远程调用
>- 一个数据库操作，直到完成
>- 一个数据库查询，直到返回结果

这种异步思想也可称为**并发**，但是它与**并行**并不一致

>[并发与并行区别](https://fastapi.tiangolo.com/zh/async/#concurrent-burgers)
>
>并发能够利用等待的空闲时间段
>
>并行只是将接收者从同步的一个变为多个，必须等任务做完，中间还是存在等待的空闲时间段，不能利用这段时间去处理其它任务

等待时间越多**异步并发**就更有意义，但是并不意味着并发优于并行，在**CPU密集型**工作上并行更加占优

>CPU密集型任务指大多由实际工作所占用，而非任务之间存在大量等待时间，常见的：
>
>- **音频**或**图像**处理
>- **计算机视觉**：一幅图像由数百万像素组成，每个像素有 3 种颜色值，处理通常需要同时对这些像素进行计算
>- **机器学习**：它通常需要大量的“矩阵”和“向量”乘法。想象一个包含数字的巨大电子表格，并同时将所有数字相乘
>- **深度学习**：只是需要做乘法的不再是单个数字电子表格，而是一大批这样的表格，在很多情况下，你需要使用一个特殊的处理器来构建和/或使用这些模型

``await``告诉python可以“暂停”执行该函数，直至执行其他操作

>await的等待不是同步意义上的阻塞，它会交出CPU的控制权让CPU先去执行其它任务，等待事件循环发出指令告诉CPU await的任务已经执行完毕了，再返回这段代码对结果进行处理

```python
burgers = await get_burgers(2)
```

`await`生效的条件是位于``async def``定义的函数内

> async函数返回的东西就叫协程

```python
async def get_burgers(number: int):
    # 执行一些异步操作来制作汉堡
    return burgers
```

那第一个`async`函数如何调用

```python
asyncio.run(主协程)
```

## FastAPI

FastAPI利用schema来标准化所有的自定义API方便后续的复用，常用POST、GET、PUT、DELETE四种操作

### 路径操作

FastAPI常使用`@app.操作("/路径")`的方式来声明不同路由下的操作函数

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

函数的参数可以由路径直接传递，操作函数也可使用类型声明享受自动的**数据类型转换和数据校验**

路径操作按顺序进行，类似路径的操作函数需要注意定义顺序，不能重复定义相同的路径操作

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/me")# 在@app.get("/users/{user_id}")后定义不起作用
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

如果想要让路径操作只接收指定的参数值可以使用`enum`

```python
from enum import StrEnum
from fastapi import FastAPI

class ModelName(StrEnum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}  # 最后会自动填充为对应的值
    if model_name.value == "lenet":			# 可以使用.value获得枚举值
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}
```

同时路径参数也允许接收路径作为参数

### 查询

声明的参数不是路径参数时会自动解释为查询参数，查询字符串是键值对的集合，这些键值对位于 URL 的`?`之后，以`&`分隔，可以享受类型声明的福利，也可设置默认值，不过此时参数就不是必选的了

```python
from typing import Annotated
from fastapi import FastAPI, Query


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Annotated[str | None, Query(max_length=50)] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

http://127.0.0.1:8000/items/?skip=0&limit=10
```

可以使用`Annotated`加上`fastapi`的`Query`对参数进行额外校验

> 这里用的是 `Query()`，因为这是一个**查询参数**。`Path()`、`Body()`、`Header()` 和 `Cookie()`，它们也接受与 `Query()` 相同的参数。

### 请求体

客户端->API=请求体，API->客户端=响应体。发送数据一般都使用`POST`

`pydantic`声明请求体，**FastAPI**分别识别请求体、路径和查询参数不用担心混用会出问题

>如果该参数也在**路径**中声明了，它就是**路径参数**
>
>如果该参数是（`int`、`float`、`str`、`bool` 等）**单一类型**，它会被当作**查询**参数
>
>如果该参数的类型声明为 **Pydantic 模型**，它会被当作**请求体**

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None		# 可选
    price: float
    tax: float | None = None			# 可选

app = FastAPI()

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
```

