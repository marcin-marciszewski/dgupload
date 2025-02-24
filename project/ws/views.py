import json

import socketio
from fastapi import FastAPI, WebSocket
from socketio.asyncio_namespace import AsyncNamespace

from . import ws_router
from project import broadcast
from project.celery_utils import get_task_info
from project.config import settings

# app = FastAPI(on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect])


@ws_router.websocket("/ws/task_status/{task_id}")
async def ws_task_status(websocket: WebSocket):
    await websocket.accept()

    task_id = websocket.scope["path_params"]["task_id"]

    async with broadcast.subscribe(channel=task_id) as subscriber:
        # just in case the task already finish
        data = get_task_info(task_id)
        await websocket.send_json(data)

        async for event in subscriber:
            await websocket.send_json(json.loads(event.message))


async def update_celery_task_status(task_id: str):
    """
    This function is called by Celery worker in task_postrun signal handler
    """
    async with broadcast.connect() as connection:
        await connection.publish(
            channel=task_id,
            message=json.dumps(
                get_task_info(task_id)
            ),  # RedisProtocol.publish expect str
        )
        await connection.disconnect()


class TaskStatusNameSpace(AsyncNamespace):
    async def on_join(self, sid, data):
        self.enter_room(sid=sid, room=data["task_id"])
        # just in case the task already finish
        await self.emit("status", get_task_info(data["task_id"]), room=data["task_id"])


def register_socketio_app(app: FastAPI):
    mgr = socketio.AsyncRedisManager(settings.WS_MESSAGE_QUEUE)
    # https://python-socketio.readthedocs.io/en/latest/server.html#uvicorn-daphne-and-other-asgi-servers
    # https://github.com/tiangolo/fastapi/issues/129#issuecomment-714636723
    sio = socketio.AsyncServer(
        async_mode="asgi", client_manager=mgr, logger=True, engineio_logger=True
    )
    sio.register_namespace(TaskStatusNameSpace("/task_status"))
    asgi = socketio.ASGIApp(
        socketio_server=sio,
    )
    app.mount("/ws", asgi)


def update_celery_task_status_socketio(task_id):
    """
    This function would be called in Celery worker
    https://python-socketio.readthedocs.io/en/latest/server.html#emitting-from-external-processes
    """
    # connect to the redis queue as an external process
    external_sio = socketio.RedisManager(settings.WS_MESSAGE_QUEUE, write_only=True)
    # emit an event
    external_sio.emit(
        "status", get_task_info(task_id), room=task_id, namespace="/task_status"
    )


@ws_router.websocket("/ws")
async def health_check(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_json({"msg": data})


@ws_router.websocket("/ws/simple")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


async def chatroom_ws_receiver(websocket: WebSocket, room_id: str):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=f"chatroom_{room_id}", message=message)


async def chatroom_ws_sender(websocket: WebSocket, room_id: str):
    async with broadcast.subscribe(channel=f"chatroom_{room_id}") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


@ws_router.websocket("/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    from .manager import manager

    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"A client says: {data}", room_id, websocket)
    except Exception as e:
        print("Got an exception ", e)
        await manager.disconnect(room_id, websocket)


@ws_router.websocket("/task/{task_id}")
async def websocket_11(websocket: WebSocket, task_id: str):
    from .manager import manager

    await manager.connect(task_id, websocket)
    try:
        data = get_task_info(task_id)
        # await manager.send_personal_message(data, websocket)
        await manager.broadcast(data, task_id, websocket)
    except Exception as e:
        print("Got an exception ", e)
        await manager.disconnect(task_id, websocket)

    #   await websocket.accept()

    # task_id = websocket.scope["path_params"]["task_id"]

    # async with broadcast.subscribe(channel=task_id) as subscriber:
    #     # just in case the task already finish
    #     data = get_task_info(task_id)
    #     await websocket.send_json(data)

    #     async for event in subscriber:
    #         await websocket.send_json(json.loads(event.message))
