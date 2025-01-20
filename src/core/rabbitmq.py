import json

import aio_pika

from core.settings import RabbitMQSettings


class RabbitMQProducer:
    def __init__(self):
        self.amqp_url = RabbitMQSettings.AMQP_URL
        self.queue_name = "avatars_queue"
        self.connection = None

    async def __aenter__(self):
        self.connection = await aio_pika.connect(self.amqp_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

    async def publish_message(self, message: dict):
        channel = await self.connection.channel()
        queue = await channel.declare_queue(self.queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
