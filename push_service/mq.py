import typing
from collections.abc import Awaitable

import aio_pika as apika


class Consumer:
    def __init__(self, channel: apika.abc.AbstractChannel):
        self._channel = channel

    async def _declare(self, queue_name: str):
        return await self._channel.declare_queue(name=queue_name, durable=True, arguments={'x-message-ttl':10})

    async def create_callback(
        self,
        callback: typing.Callable[
            [apika.abc.AbstractIncomingMessage], Awaitable[typing.Any]
        ],
        queue_name: str,
    ):
        queue = await self._declare(queue_name=queue_name)
        await self._channel.set_qos(prefetch_count=1)
        await queue.consume(
            callback=callback,
        )
