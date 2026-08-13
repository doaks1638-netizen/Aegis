import asyncio

import aio_pika as apika
from httpx2 import AsyncClient, ConnectError
from settings import settings


async def send(msg: apika.abc.AbstractIncomingMessage):
    try:
        async with AsyncClient() as client:
            for _ in range(3):
                try:
                    async with asyncio.timeout(10):
                        send_message_url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
                        payload = {
                            "chat_id": settings.TG_CHAT_ID,
                            "text": f"<b>📢❗🚨 ATTENTION! SERVICE ERROR!</b>\n\nDetails:\n{msg.body.decode()}",
                            "parse_mode": "HTML",
                        }
                        await client.post(url=send_message_url, data=payload)
                        break
                except ConnectError:
                    continue
                except asyncio.TimeoutError:
                    continue
            await asyncio.sleep(delay=settings.WARN_WAIT_TIME_SEC)
            await msg.ack()
    finally:
        await msg.reject(requeue=True)
