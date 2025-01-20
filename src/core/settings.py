import os


class RabbitMQSettings:
    AMQP_URL = os.getenv("AMQP_URL")
