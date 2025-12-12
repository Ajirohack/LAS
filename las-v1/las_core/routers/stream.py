"""
Stream Router - Real-time streaming support via SSE and WebSocket.

Provides:
- Server-Sent Events (SSE) for HTTP-based streaming
- WebSocket support for bidirectional communication
- Integration with LiteLLM for streaming completions
"""

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from typing import Dict, Any, List
from sources.logger import Logger

router = APIRouter()
logger = Logger("stream.log")

# Global queue for broadcasting messages (simplified for single-instance)
# In production, use Redis Pub/Sub
message_queue = asyncio.Queue()

# Connected WebSocket clients
connected_clients: List[WebSocket] = []


# ============== SSE (Server-Sent Events) ==============

async def event_generator():
    """Generate SSE events from the message queue."""
    while True:
        try:
            message = await message_queue.get()
            yield {
                "event": "message",
                "id": message.get("id", "msg"),
                "retry": 15000,
                "data": json.dumps(message)
            }
        except asyncio.CancelledError:
            break


@router.get("/stream")
async def stream(request: Request):
    """
    Server-Sent Events endpoint for real-time agent updates.
    
    Connect using EventSource in JavaScript:
    ```javascript
    const eventSource = new EventSource('/api/v1/stream/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
    };
    ```
    """
    return EventSourceResponse(event_generator())


# ============== WebSocket Support ==============

@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional real-time communication.
    
    Connect using WebSocket in JavaScript:
    ```javascript
    const ws = new WebSocket('ws://localhost:7777/api/v1/stream/ws/stream');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
    };
    ws.send(JSON.stringify({ type: 'query', content: 'Hello!' }));
    ```
    """
    await websocket.accept()
    connected_clients.append(websocket)
    logger.info(f"WebSocket client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": "Invalid JSON message"
                })
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming WebSocket messages and route to appropriate handlers."""
    msg_type = message.get("type", "unknown")
    
    if msg_type == "query":
        # Handle chat query with streaming response
        await handle_streaming_query(websocket, message)
    elif msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    elif msg_type == "subscribe":
        # Subscribe to specific event types
        await websocket.send_json({
            "type": "subscribed",
            "data": message.get("channels", [])
        })
    else:
        await websocket.send_json({
            "type": "error",
            "data": f"Unknown message type: {msg_type}"
        })


async def handle_streaming_query(websocket: WebSocket, message: Dict[str, Any]):
    """Handle a streaming chat query via WebSocket."""
    try:
        content = message.get("content", "")
        model = message.get("model")
        provider = message.get("provider")
        
        if not content:
            await websocket.send_json({
                "type": "error",
                "data": "Missing 'content' in query"
            })
            return
        
        # Try to use LiteLLM for streaming
        try:
            from services.litellm_service import get_litellm_service
            svc = get_litellm_service()
            
            messages = [{"role": "user", "content": content}]
            
            # Stream the response
            response = svc.chat_completion(
                messages=messages,
                model=model,
                provider=provider,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    await websocket.send_json({
                        "type": "token",
                        "data": chunk.choices[0].delta.content
                    })
            
            await websocket.send_json({"type": "complete", "data": None})
            
        except ImportError:
            # Fallback if LiteLLM not available
            await websocket.send_json({
                "type": "error",
                "data": "LiteLLM service not available"
            })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "data": str(e)
            })
            
    except Exception as e:
        logger.error(f"Streaming query error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": f"Query failed: {e}"
        })


# ============== Broadcasting Helpers ==============

async def broadcast_event(event_type: str, data: dict):
    """
    Broadcast event to both SSE queue and WebSocket clients.
    """
    event = {
        "type": event_type,
        "data": data
    }
    
    # Add to SSE queue
    await message_queue.put(event)
    
    # Send to all WebSocket clients
    disconnected = []
    for client in connected_clients:
        try:
            await client.send_json(event)
        except Exception:
            disconnected.append(client)
    
    # Clean up disconnected clients
    for client in disconnected:
        connected_clients.remove(client)


async def broadcast_token(token: str):
    """Broadcast a token event for streaming responses."""
    await broadcast_event("token", token)


async def broadcast_thought(thought: str):
    """Broadcast a thought/reasoning event."""
    await broadcast_event("thought", {"content": thought})


async def broadcast_tool_call(tool_name: str, args: dict, result: Any = None):
    """Broadcast a tool call event."""
    await broadcast_event("tool", {
        "name": tool_name,
        "arguments": args,
        "result": result
    })


async def broadcast_complete(response: str = None, usage: dict = None):
    """Broadcast completion event."""
    await broadcast_event("complete", {
        "response": response,
        "usage": usage
    })


async def broadcast_error(error: str):
    """Broadcast error event."""
    await broadcast_event("error", {"message": error})


# ============== Client Stats ==============

@router.get("/stream/stats")
async def stream_stats():
    """Get streaming connection statistics."""
    return {
        "sse_queue_size": message_queue.qsize(),
        "websocket_clients": len(connected_clients),
    }
