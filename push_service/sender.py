import aio_pika as apika
from httpx2 import AsyncClient
from settings import settings


async def send(msg: apika.abc.AbstractIncomingMessage):
    try:
        async with AsyncClient() as client:
            send_message_url = (
                f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
            )
            payload = {
                "chat_id": settings.TG_CHAT_ID,
                "text": f"""
**ATTENTION! SERVICE ERROR!**

Details:

{msg.body.decode()}

from Aegis            
            """,
            }
            await client.post(send_message_url, data=payload)
            await msg.ack()
    finally:
        await msg.reject(requeue=True)
