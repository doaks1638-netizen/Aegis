import typing

import aio_pika as apika
from fastapi import Depends
from fastapi.requests import HTTPConnection


class Pubsliher:
    def __init__(self, channel: apika.abc.AbstractChannel):
        self._channel = channel

    async def _declare(self, queue_name: str):
        return await self._channel.declare_queue(name=queue_name, durable=True, arguments={'x-message-ttl':10})

    async def publish_msg(self, msg: str, routing_key: str):
        await self._declare(queue_name=routing_key)
        await self._channel.default_exchange.publish(
            message=apika.Message(
                body=msg.encode(), delivery_mode=apika.DeliveryMode.PERSISTENT
            ),
            mandatory=True,
            routing_key=routing_key,
        )


async def get_publisher(conn: HTTPConnection):
    return Pubsliher(channel=(await conn.app.state.mq.channel()))


type PubsliherDepends = typing.Annotated[Pubsliher, Depends(get_publisher)]
