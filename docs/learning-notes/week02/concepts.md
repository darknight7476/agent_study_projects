# 本周理论知识

## [同步与异步](../week01/concepts.md)

同步任务是阻塞式顺序串行完成，异步任务会并发等待完成任务消耗时间只取决于最长的任务

| 对比维度       | 同步             | 异步                 |
| -------------- | ---------------- | -------------------- |
| 执行方式       | 按顺序执行       | 任务交替推进         |
| 等待期间       | 通常阻塞当前线程 | 可以执行其他任务     |
| 代码复杂度     | 较低             | 相对较高             |
| I/O 密集型任务 | 效率可能较低     | 通常效率较高         |
| CPU 密集型任务 | 适合直接执行     | 单纯异步不一定有优势 |

## 协程

可以暂停执行并在之后恢复执行的函数

在python中涉及协程的基础库是`asyncio`大多异步框架都基于此进行搭建，使用`async`和`await`标识异步函数，真正允许不能直接调用`main()`，`asyncio`提供了几种方法

```python
# 运行最外层入口函数
asyncio.run() 

# 对协程执行 await
async def main():
    await say_after(1, 'hello')
    await say_after(2, 'world')

# asyncio.create_task()用来并发运行多个协程
async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))
    task2 = asyncio.create_task(
        say_after(2, 'world'))
    await task1
    await task2

# 使用asyncio.TaskGroup类替换
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            say_after(1, 'hello'))
        task2 = tg.create_task(
            say_after(2, 'world'))
```

能够使用`await`的三类可等待对象

1. 协程
2. 任务
3. Future

>协程包括协程函数(定义为async def的函数)和协程对象(调用协程函数返回的对象)
>
>任务是由 `asyncio.create_task() `等函数封装的协程，能够自动并发调度协程
>
>Future表示一个异步操作的结果

## 创建任务

`asyncio.create_task(coro, ***, name=None, context=None)`函数被用来将协程封装为Task并调度执行

`asyncio.TaskGroup.create_task()` 可允许方便地等待包含多个相关任务的分组

```python
async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(some_coro(...))
        task2 = tg.create_task(another_coro(...))
    print("Both tasks have completed now.")
```

>`async with` 语句将等待分组中的所有任务结束。在等待期间，仍可将新任务添加到分组中,一旦最后的任务完成并退出 `async with` 代码块，将无法再向分组添加新任务
>
>保存一个指向此函数的结果的引用，以避免任务在执行过程中消失。事件循环将只保留对任务的弱引用，未在其他地方被引用的任务可能在任何时候被作为垃圾回收

`asyncio.gather(*aws, return_exceptions=False)`可以并发运行aws序列中的可等待对象，如果所有可等待对象都成功完成，结果将是一个由所有返回值聚合而成的列表。结果值的顺序与aws 中可等待对象的顺序一致可以被`Task.Group`取代，出现异常不会直接取消全部任务

`coroutine asyncio.to_thread(func, /, **args, ***kwargs)`在不同的线程中异步地运行函数 *func*，避免在协程中阻塞事件循环

> 协程和Task的区别	
>
> 协程的特点：
>
> - 是惰性的，创建后不会自动执行
> - 需要被 `await`，或者被包装成 `Task` 才会运行
>
> `Task` 是 asyncio 中的调度单位其特点为：
>
> - 包装协程
> - 可被事件循环调度(在创建完的那一刻就已经在事件循环中开始执行了)
> - 可以并发运行
> - 可以 `await`(这里await作用不再是启动，而是为了等待结束并获取结果)
>
> > 协程是“要做的事情”，Task 是“已经交给事件循环去安排执行的事情”

`asyncio.wait_for(aw, timeout)`等待aw完成，timeout秒后超时，aw是协程会自动执行,注意超时后会等待aw协程真正被取消

`asyncio.wait(aws, *, timeout=None, return_when=ALL_COMPLETED)`并发地运行*可迭代对象aws中的实例*并进入阻塞状态直到满足 *return_when* 所指定的条件：`FIRST_COMPLETED`、`FIRST_EXCEPTION`、`ALL_COMPLETED`

`asyncio.as_completed(aws, *, timeout=None)`(产生任务的生成器不可被用作 aws 可迭代对象)返回一个产生协程的迭代器，谁先完成就先处理谁。

## 事件循环

它负责：

1. 管理多个协程任务
2. 调度协程开始执行
3. 检查哪些任务正在等待
4. 当等待条件满足时，恢复相应任务
5. 不断循环，直到任务完成

| 结构                      | 作用                                             |
| :------------------------ | :----------------------------------------------- |
| **就绪队列 ready queue**  | 存放“现在就可以执行”的回调（callback）           |
| **定时器堆 timer heap**   | 存放 `call_later` / `sleep` 这类定时任务         |
| **I/O 多路复用 selector** | 监听 socket 等 I/O 事件（epoll / kqueue / IOCP） |

```python
while True:
    # 1. 计算最近的定时器还有多久到期，作为 select 的超时时间
    timeout = 计算到下一个定时器的剩余时间()

    # 2. 等待 I/O 事件，最多等 timeout
    events = selector.select(timeout)

    # 3. 把到期的定时器回调、I/O 回调放进就绪队列
    把到期的定时器回调加入 ready
    把就绪的 I/O 回调加入 ready

    # 4. 依次执行就绪队列里的所有回调
    for callback in ready:
        callback()
```

本身协程的执行还是由Task内部进行完成，示例如下：

```text
asyncio.run(main())
  └─ 创建事件循环，把 main 协程包装成 Task，放入就绪队列

事件循环 run_forever()
  └─ 从 ready 取出 main 的 Task.__step
       └─ main_coro.send(None)
            ├─ create_task(A)  → A 的 Task.__step 加入 ready
            ├─ create_task(B)  → B 的 Task.__step 加入 ready
            ├─ print("任务已经创建")
            └─ await task1  → main 挂起，等 task1 完成

事件循环继续
  └─ 取出 A 的 Task.__step → A_coro.send(None) → 执行到 sleep(2)，注册定时器，挂起
  └─ 取出 B 的 Task.__step → B_coro.send(None) → 执行到 sleep(1)，注册定时器，挂起
  └─ 就绪队列空了，selector.select(超时=1s)

1 秒后
  └─ B 的定时器到期 → 把 B 的 __wakeup 放入 ready
  └─ 取出 B 的 __wakeup → B_coro.send(None) → 打印 "B: 完成" → 协程结束 → task2 设置结果
       └─ task2 完成 → 触发 main 上挂的 await task2 的回调（但 main 还在等 task1）

2 秒后
  └─ A 的定时器到期 → 把 A 的 __wakeup 放入 ready
  └─ 取出 A 的 __wakeup → A_coro.send(None) → 打印 "A: 完成" → 协程结束 → task1 设置结果
       └─ task1 完成 → main 被唤醒，加入 ready

事件循环取出 main 的 __wakeup
  └─ main_coro.send(None) → await task1 返回 → 执行 await task2（已完成，立即返回）→ main 结束
```

## 同步原语

`asyncio.Lock`实现互斥锁的类保证对共享资源的独占

- **acquire**()：获取锁。一个以上的协程在等待锁，被执行的协程将是第一个开始等待锁的协程

- **release**()

  释放锁。当锁为 *locked* 时，将其设为 *unlocked* 并返回

- **locked**()

  如果锁为 *locked* 则返回 `True`

```python
lock = asyncio.Lock()

# ... later
async with lock:
    # access shared state
```

`asyncio.Semaphore` 管理一个内部计数器，每次 `acquire()` 减一，`release()` 加一，计数器为 0 时后续 `acquire()` 会阻塞等待。

解决的是“**同时最多跑 N 个**”的问题，而不是“每秒最多跑 N 个”

```python
semaphore = asyncio.Semaphore(3)

async with semaphore:
    print(f"用户 {user_id} 开始请求")
```

## PostgreSQL

