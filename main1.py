from fastapi import FastAPI
import asyncio
import time

app = FastAPI()


# ============================================================
# Sync(동기) / Async(비동기) 대기시간 테스트
# ============================================================


# Async(비동기) 방식
@app.get("/slow-async", tags=["학습용"], summary="비동기 대기 실습")
async def slow_async():
    """비동기 방식으로 3초 동안 대기한 뒤 완료 메시지를 반환합니다."""
    await asyncio.sleep(3)

    return {
        "type": "async",
        "message": "3초 대기 완료"
    }


# Sync / Blocking(동기 / 블로킹) 방식
@app.get("/slow-block", tags=["학습용"], summary="동기 블로킹 대기 실습")
def slow_block():
    """잠금 구간에서 동기 방식으로 3초 동안 대기한 뒤 완료 메시지를 반환합니다."""
    with block_lock:
        time.sleep(3)

    return {
        "type": "block",
        "message": "3초 대기 완료"
    }
