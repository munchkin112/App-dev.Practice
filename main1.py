from fastapi import FastAPI
import asyncio
import time

app = FastAPI()


# ============================================================
# Sync(동기) / Async(비동기) 대기시간 테스트
# ============================================================


# Async(비동기) 방식
@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3)

    return {
        "type": "async",
        "message": "3초 대기 완료"
    }


# Sync / Blocking(동기 / 블로킹) 방식
@app.get("/slow-block")
def slow_block():
    with block_lock:
        time.sleep(3)

    return {
        "type": "block",
        "message": "3초 대기 완료"
    }