from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from sources.logger import Logger

router = APIRouter()
logger = Logger("stream.log")

# Global queue for broadcasting messages (simplified for single-instance)
# In production, use Redis Pub/Sub
message_queue = asyncio.Queue()

async def event_generator():
    while True:
        # If client disconnects, this will throw
        try:
            message = await message_queue.get()
            yield {
                "event": "message",
                "id": "message_id",
                "retry": 15000,
                "data": json.dumps(message)
            }
        except asyncio.CancelledError:
            break

@router.get("/stream")
async def stream(request: Request):
    """
    Server-Sent Events endpoint for real-time agent updates.
    """
    return EventSourceResponse(event_generator())

async def broadcast_event(event_type: str, data: dict):
    """
    Helper to push events to the queue.
    """
    await message_queue.put({
        "type": event_type,
        "data": data
    })
