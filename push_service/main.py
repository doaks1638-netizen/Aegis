import asyncio

import aio_pika as apika
import uvloop
from mq import Consumer
from sender import send
from settings import settings


async def main():
    async with await apika.connect_robust(url=settings.get_mq_url()) as conn:
        consumer = Consumer(channel=await conn.channel())
        await consumer.create_callback(callback=send, queue_name="errors")
        await asyncio.Future()


if __name__ == "__main__":
    uvloop.run(main())
