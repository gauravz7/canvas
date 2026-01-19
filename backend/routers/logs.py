from fastapi import APIRouter
from services.log_service import log_service
from typing import List, Dict

from sse_starlette.sse import EventSourceResponse
import json
import asyncio

router = APIRouter()

@router.get("", response_model=List[Dict])
async def get_logs(limit: int = 100):
    return log_service.get_logs(limit)

@router.get("/stream")
async def stream_logs():
    async def event_generator():
        async for q in log_service.subscribe():
            while True:
                log_entry = await q.get()
                yield {
                    "data": json.dumps(log_entry)
                }

    return EventSourceResponse(event_generator())
