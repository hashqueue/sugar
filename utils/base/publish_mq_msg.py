# -*- coding: utf-8 -*-
import logging
import traceback

import pika
from pika import DeliveryMode

logger = logging.getLogger('my_debug_logger')

"""
如何在Django视图中使用
from utils.base.publish_mq_msg import publish_message
from sugar.settings import env

publish_message(env('RABBITMQ_USER'), env('RABBITMQ_PASSWORD'), env('RABBITMQ_HOST'), env('RABBITMQ_PORT'),
                        'test_exchange', 'test_routing_key', 'name')
"""


def publish_message(mq_user: str, mq_pwd: str, mq_host: str, mq_port: int, exchange: str, routing_key: str,
                    message_body: str, exchange_type: str = 'direct', durable: bool = True):
    """
    Publish message to mq
    @param mq_user: mq user
    @param mq_pwd: mq password
    @param mq_host: mq host
    @param mq_port: mq port
    @param exchange: mq exchange
    @param routing_key: mq routing key
    @param message_body: mq message body
    @param exchange_type: mq exchange type
    @param durable: mq durable - True -> Survive a reboot of RabbitMQ; False -> Not survive a reboot of RabbitMQ
    @return:
    """
    try:
        credentials = pika.PlainCredentials(mq_user, mq_pwd)
        parameters = pika.ConnectionParameters(host=mq_host, port=mq_port, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange,
                                 exchange_type=exchange_type,
                                 durable=durable)
        # DeliveryMode.Transient - Message will be lost if RabbitMQ quits or crashes
        # DeliveryMode.Persistent - Message will survive a reboot of RabbitMQ
        channel.basic_publish(exchange, routing_key, message_body.encode('utf-8'),
                              pika.BasicProperties(content_type='text/plain', delivery_mode=DeliveryMode.Transient))
        logger.info(f'Publish message to mq successfully, exchange: {exchange}, routing_key: {routing_key}')
        connection.close()
    except Exception as e:
        logger.error(f'Exception happened when publish message: {e}, detail: {traceback.format_exc()}')
