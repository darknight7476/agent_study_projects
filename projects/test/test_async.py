import asyncio
import time
import random


"""
要求：
1. 同时处理 20 个请求。
2. 最大并发数量为 3。
3. 每个请求最多等待 5 秒。
4. 单个请求失败不能导致其他结果丢失。
5. 记录每个请求的执行时间。
"""
semaphore = asyncio.Semaphore(3)


async def fetch(user_id):
    async with semaphore:
        start = time.perf_counter()
        print(f"用户 {user_id} 开始请求")

        await asyncio.sleep(random.uniform(0.5, 2.0))
        if random.random() < 0.2:
            print(f"用户 {user_id} 请求失败")
            raise RuntimeError(f"用户 {user_id} 请求失败")
        print(f"用户 {user_id} 结束请求")
        print(f"任务耗时:{time.perf_counter() - start}")
        return f"用户 {user_id} 的结果"


async def main():
    tasks = [
        asyncio.create_task(fetch(i))
        for i in range(20)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(results)


asyncio.run(main())

