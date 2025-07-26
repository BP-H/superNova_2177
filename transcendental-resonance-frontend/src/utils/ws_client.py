import asyncio
import json
from typing import Callable, Awaitable

import websockets

HOST = 'ws://localhost:8080'


def start_client(path: str, handler: Callable[[dict], Awaitable[None]]) -> None:
    async def _run() -> None:
        uri = f"{HOST}{path}"
        try:
            async with websockets.connect(uri) as ws:
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                    except json.JSONDecodeError:
                        data = {'message': msg}
                    await handler(data)
        except Exception:
            pass
    asyncio.create_task(_run())
