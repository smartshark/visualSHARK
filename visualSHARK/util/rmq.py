#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import pika
from django.conf import settings


def send_to_user(rkey, data):
    """This is only for the websocket."""
    server = settings.QUEUE['server']
    port = settings.QUEUE['port']
    vhost = settings.QUEUE['vhost']
    user = settings.QUEUE['user']
    password = settings.QUEUE['password']
    ssl = settings.QUEUE['ssl']

    if not server:
        raise Exception('no queue config!')

    credentials = pika.PlainCredentials(user, password)

    parameters = pika.ConnectionParameters(server, int(port), vhost, credentials, ssl=ssl)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.basic_publish(exchange='amq.topic',
                          routing_key=str(rkey),  # we may pass a uuid directly
                          body=json.dumps(data))
    connection.close()


def send_to_queue(queue, data):
    server = settings.QUEUE['server']
    port = settings.QUEUE['port']
    vhost = settings.QUEUE['vhost']
    user = settings.QUEUE['user']
    password = settings.QUEUE['password']
    ssl = settings.QUEUE['ssl']

    if not server:
        return

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(server, int(port), vhost, credentials, ssl=ssl)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(exchange='',
                          routing_key=queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
                          )
    connection.close()
