"""Module for test queue management"""

from typing import Callable

import asyncio
from pytest_mock import MockerFixture

from internal.models import User
from internal.queue_manager import QueueManager, QueueConn, USER_QUEUE


DATA_POINT = User(index=1, created_at="2022-01-01")


def test_queue_manager_enqueue_user(mocker: MockerFixture) -> None:
    queue_conn = mocker.MagicMock(QueueConn)
    queue_conn.send_message = mocker.AsyncMock()
    queue_conn.send_message.return_value = None

    async def do():
        manager = QueueManager(queue_conn)

        await manager.enqueue_user(DATA_POINT)
        queue_conn.send_message.assert_called_once()
        queue_conn.send_message.assert_awaited_with(
            USER_QUEUE, DATA_POINT.model_dump_json()
        )

    asyncio.run(do())


def test_queue_manager_process_user_queue_message(
    mocker: MockerFixture,
) -> None:

    async def my_process_manager(queue_name, func) -> None:
        assert queue_name == USER_QUEUE
        assert isinstance(func, Callable)
        await func(DATA_POINT.model_dump_json())

    queue_conn = mocker.MagicMock(QueueConn)
    queue_conn.process_message = my_process_manager

    async def test_func(user: User) -> None:
        assert isinstance(user, User)
        assert user.index == 1
        assert user.created_at == "2022-01-01"

    async def do_assert():
        manager = QueueManager(queue_conn)
        await manager.process_user_queue_message(test_func)

    asyncio.run(do_assert())
