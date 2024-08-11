"""
Module for dealing if queue
"""

import asyncio
import functools
import json
from typing import Annotated, Awaitable, Callable

import aio_pika
from fastapi import Depends

from internal.models import User
from internal.settings import ApiSettingsDI


USER_QUEUE = "process_user_request"


class QueueConn:
    """Manages connection with queue"""

    def __init__(self, settings: ApiSettingsDI) -> None:
        self.settings = settings
        self.conn = None

    async def _connect(self) -> None:
        if self.conn is not None:
            return

        self.conn = await aio_pika.connect_robust(self.settings.amqp_dsn)

    async def send_message(self, queue_name: str, message: str) -> None:
        """Send any message to queue"""

        await self._connect()
        async with self.conn:
            channel = await self.conn.channel()
            queue = await channel.declare_queue(queue_name)
            await channel.default_exchange.publish(
                aio_pika.Message(message.encode()), routing_key=queue.name
            )

    async def process_message(
        self, queue_name: str, func: Callable[[str], Awaitable[None]]
    ) -> None:
        """Process sended message"""

        await self._connect()

        async def on_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                await func(message.body.decode())

        async with self.conn:
            channel = await self.conn.channel()
            queue = await channel.declare_queue(queue_name)

            await queue.consume(on_message)

        await asyncio.Future()


class QueueManager:
    """Manage sendind and receive data from queue"""

    def __init__(
        self, connection: Annotated[QueueConn, Depends(QueueConn)]
    ) -> None:
        self.connection: QueueConn = connection

    async def enqueue_user(self, user: User) -> None:
        """Send user to be processed in async way"""

        await self.connection.send_message(USER_QUEUE, user.model_dump_json())

    async def process_user_queue_message(
        self, func: Callable[[User], Awaitable[None]]
    ) -> None:
        """Process all income user messages in given callback"""

        async def wrapper(income: str) -> None:
            await func(User(**json.loads(income)))

        await self.connection.process_message(USER_QUEUE, wrapper)
