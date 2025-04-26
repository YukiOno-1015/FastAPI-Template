#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from utils.firebase_auth import verify_firebase_token_ws

router = APIRouter()
LOGGER = logging.getLogger("uvicorn.routers.ws")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
        LOGGER.debug(f"New connection accepted: {ws.client}")

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)
            LOGGER.debug(f"Connection removed: {ws.client}")

    async def broadcast(self, msg: str):
        """
        ── 全クライアントに msg をそのまま送信 ──
        """
        for conn in self.active_connections:
            try:
                await conn.send_text(msg)
                LOGGER.debug(f"Sent to {conn.client}: {msg}")
            except Exception as e:
                LOGGER.error(f"Failed to send to {conn.client}: {e}")


manager = ConnectionManager()


@router.websocket("/ws/chat/{client_id}")
async def chat_endpoint(websocket: WebSocket, client_id: int):
    """
    - トークン検証後 accept
    - 生のメッセージを全員に broadcast
    """
    # 1) トークン検証 (内部で ws.accept()/close() してくれます)
    user_data = await verify_firebase_token_ws(websocket)

    # 2) 正式にコネクション登録
    await manager.connect(websocket)
    LOGGER.info(f"Client #{client_id} (uid={user_data['uid']}) connected")

    try:
        while True:
            # 3) クライアントから生メッセージを受け取る
            data = await websocket.receive_text()
            LOGGER.debug(f"[{user_data['uid']}] recv: {data!r}")

            # 4) 受け取った「生データ」をそのまま全員に配信
            await manager.broadcast(data)

            # （必要ならエコーを追加）
            # await websocket.send_text(f"You said: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        LOGGER.info(f"Client #{client_id} disconnected")
        # 切断通知も生データとして流したい場合
        await manager.broadcast(f"Client #{client_id} left chat")

    except Exception as e:
        LOGGER.error(f"Unexpected error with Client #{client_id}: {e}")
        manager.disconnect(websocket)
