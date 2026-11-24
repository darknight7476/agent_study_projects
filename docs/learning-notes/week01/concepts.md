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
    
# 除了常规的定义方式还能够使用Field定义
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
```

``Annotated``支持在类型提示中加入额外的**元数据**

```python
def say_hello(name: Annotated[str, "this is just metadata"]) -> str:
```

pydantic还支持额外的JSON Schema，会原样添加到模型的JSON Schema，也可以直接在`Filed`中声明

```python
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }
    
class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])
```

`model_dump`能够返回模型数据的`dict`配合`**dict`能够将其解包为键和值作为关键字参数直接传递

```python
# 利用其它pydantic模型数据生成新的pydantic模型
user_dict = user_in.model_dump()
UserInDB(**user_dict)
'''
UserInDB(
    username=user_dict["username"],
    password=user_dict["password"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
)
'''


# 还支持额外添加关键字
UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
'''UserInDB(
    username=user_dict["username"],
    password=user_dict["password"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
    hashed_password=hashed_password,
)
'''
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

### 查询

声明的参数不是路径参数时会自动解释为查询参数，查询字符串是键值对的集合，这些键值对位于 URL 的`?`之后，以`&`分隔，可以享受类型声明的福利，也可设置默认值，不过此时参数就不是必选的了(**有且只有设置默认值之后才会变成可选**，也不支持除默认值外设置为`None`)

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

> 这里用的是 `Query()`，因为这是一个**查询参数**。`Path()`、`Body()`、`Header()` 和 `Cookie()`，它们也接受与 `Query()` 相同的参数

声明类型为`list`的查询参数需要显式使用`Query()`,否则会被识别为请求体

```python
@app.get("/items/")
async def read_items(q: Annotated[list[str] | None, Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items

# 也可以不指明list内类型，此时fastapi不会检查里面的类型
@app.get("/items/")
async def read_items(q: Annotated[list, Query()] = []):
    query_items = {"q": q}
    return query_items

# Query支持更多参数声明
# 别名参数能够使用alias声明
"""
Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            alias = 'item-query',
            deprecated=True, # 说明参数已弃用
            include_in_schema = False # 将不再OpenAPI中排除
            ge = 1, # 数值校验同理还有gt和le
        ),
"""


```

还可以使用自定义校验函数结合`AfterValidator`进行额外校验

```python
ef check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items/")
async def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}
```

在需要多个查询参数的时候可以将他们归并到一个`pydantic`模型中简化代码

可以使用 Pydantic 的模型配置来 `forbid` 任何 `extra` 字段**限制**要接收的查询参数

```python
class Pagination(BaseModel):
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)


class Filters(BaseModel):
    tags: list[str] = []


@app.get("/items/")
def read_items(
    pagination: Annotated[Pagination, Query()],
    filters: Annotated[Filters, Query()],
    search: str | None = None,
):
    return {"pagination": pagination, "filters": filters, "search": search}
# 在查询时不用使用函数中声明的变量名，而是按照类内属性传输
# 如果pydantic模型共享参数每个模型都会单独验证
```

### 路径

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

路径参数校验使用`Path`与`Query`参数一致

> 路径参数是必需的，使用`Path`声明的不能有默认值

路径操作中可以使用`status_code`声明HTTP状态码

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

请求体可以包含显式的`null`值

当存在多个`pydantic`请求体参数时请求体构建需要带上对应的键名(在单个请求体模型时也希望请求体格式也是键值对,`Annotated[Item, Body(embed=True)]`)

```python
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    }
}
```

针对单一值做请求体，fastapi提供`Body`声明

OpenAPI也支持提供示例

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
                {
                    "name": "Bar",
                    "price": "35.4",
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results


"""
summary：该示例的简短描述。
description：较长描述，可以包含 Markdown 文本。
value：实际展示的示例，例如一个 dict。
externalValue：value 的替代项，指向该示例的 URL。不过它的工具支持度可能不如 value
"""
@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
```

### Cookie和Header

`Header`和`Cookie`声明和`Query`和`Path`一样,一定要加入`Cookie()、Header()`,`JavaScript`一般接触不到cookie

标准请求头使用-连接，但是python中是不允许的，所以`Header`会自动把_改为-

请求头同时也是不区分大小写的

它们同样支持pydantic

```python
class Cookies(BaseModel):
    model_config = {"extra": "forbid"}
    
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies| None, Cookie()]= None):
    return cookies

class ClientHeaders(BaseModel):
    x_client_name: str
    x_client_version: str


@app.get("/items/")
async def read_items(client: Annotated[ClientHeaders | None, Header()] = None):
    return client
```

### 响应

直接使用类型注解指明输出类型，自动完成校验

```python
@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item
```

如果希望返回的数据与声明类型不完全一致，但是希望使用pydantic模型的校验功能可以在路径操作钟加入装饰器参数`response_model`

>**函数返回注解 (`-> Any` 或 `-> dict`)**：反映函数**内部**的真实返回类型，让静态检查工具满意，但是此时无法生成对外的API文档来进行校验
>
>**装饰器参数 (`response_model=UserPublic`)**：明确告诉 FastAPI 对外**运行时**的响应，将内部运行和外部声明解耦，可以保证响应输出严格按照模型指定内容输出，不存在数据泄露
>
>但是使用response_model之后我们就失去了对返回类型的检查支持

```python
@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item
```

为了保持对返回类型的检查支持，我们可以通过对子类继承的方法实现上述功能，但要注意必须是pydantic类或者Response类及其子类，dict等是不支持的。 `response_model=None` 可以禁用fastapi执行文档校验和数据过滤

```python
class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    return user
```

同样在定义类时可以使用默认值，如果想要在返回的响应中不要出现冗长的默认值，可以使用 `response_model_exclude_unset=True`，这样响应只会包含被显式设置的值

### 流式传输

常使用`JSON Lines`作为流式输出常用格式，响应类型为`application/jsonl`

```python
{"name": "Plumbus", "description": "A multi-purpose household device."}
{"name": "Portal Gun", "description": "A portal opening device."}
{"name": "Meeseeks Box", "description": "A box that summons a Meeseeks."}
```

对于非一次性输出完整内容可以使用`yield`生成器，对于其输出类型已知可以使用Iterable进行输出类型声明，即便不用fastapi也会自己转换数据格式

除此以外还可以使用**SSE(服务器发送事件)**响应类型为`text/event-stream` 

```python
data: {"name": "Portal Gun", "price": 999.99}
# 注意中间多一个空行
data: {"name": "Plumbus", "price": 32.99}
```

```python
class Item(BaseModel):
    name: str
    description: str | None

items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]

@app.get("/items/stream", response_class=EventSourceResponse)
async def sse_items() -> AsyncIterable[Item]:
    for item in items:
        yield item
```

如果需要设置SSE字段可以使用`ServerSentEvent`,如果想要发送原始数据可以使用 `raw_data` 

```python
@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(comment="stream of item updates")
    for i, item in enumerate(items):
        yield ServerSentEvent(data=item, event="item_update", id=str(i + 1), retry=5000)
        
@app.get("/logs/stream", response_class=EventSourceResponse)
async def stream_logs() -> AsyncIterable[ServerSentEvent]:
    logs = [
        "2025-01-01 INFO  Application started",
        "2025-01-01 DEBUG Connected to database",
        "2025-01-01 WARN  High memory usage detected",
    ]
    for log_line in logs:
        yield ServerSentEvent(raw_data=log_line)
        
# data 和 raw_data 是互斥的
```

