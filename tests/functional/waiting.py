import asyncio

from utils.waiters import wait_for_es, wait_for_redis

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(wait_for_es(), wait_for_redis()))
    loop.close()
