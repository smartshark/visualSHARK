import json

import pika

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from visualSHARK.models import VSJob
from visualSHARK.util.remote import RemoteShark
# from visualSHARK.util.local import create_vcs_history


class Command(BaseCommand):
    """Django integrated worker process used for debugging.

    This worker consumes jobs from the rabbitmq jobs queue, executes them and persists the results in the django database.
    """

    help = 'Worker Process'

    def add_arguments(self, parser):
        pass

    def consume(self, channel, method_frame, header_frame, body):
        dat = json.loads(body)
        self.stdout.write('executing job {}'.format(dat['job_type']))

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        res = False
        msg = {}
        if dat['job_type'] == 'collect_revision':
            r = RemoteShark(dat['data']['api_url'], dat['data']['api_key'], dat['data']['substitutions'])
            res, msg = r.collect_revision(dat['data']['project_mongo_ids'], dat['data']['plugin_ids'], dat['data'])
        elif dat['job_type'] == 'collect_other':
            r = RemoteShark(dat['data']['api_url'], dat['data']['api_key'], dat['data']['substitutions'])
            res, msg = r.collect_other(dat['data']['project_mongo_ids'], dat['data']['plugin_ids'], dat['data'])
        elif dat['job_type'] == 'test_connection_worker':
            res, msg = True, {'msg': 'worker works'}
        elif dat['job_type'] == 'test_connection_servershark':
            r = RemoteShark(dat['data']['api_url'], dat['data']['api_key'], dat['data']['substitutions'])
            res, msg = r.test_connection(dat['data'])
        # elif dat['job_type'] == 'create_vcs_history':
        #     res, msg = create_vcs_history(dat['data'])

        # get job save result
        job = VSJob.objects.get(pk=dat['job_id'])
        job.executed_at = timezone.now()
        job.result = json.dumps(msg)
        if not res:
            job.error_count = 1
        job.save()

        # acknowledge job
        # channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def handle(self, *args, **options):
        credentials = pika.PlainCredentials(settings.QUEUE['user'], settings.QUEUE['password'])
        parameters = pika.ConnectionParameters(settings.QUEUE['server'], int(settings.QUEUE['port']), settings.QUEUE['vhost'], credentials, ssl=settings.QUEUE['ssl'])

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=settings.QUEUE['job_queue'], durable=True)
        channel.basic_consume(self.consume, settings.QUEUE['job_queue'])
        self.stdout.write('listening...')

        try:
            channel.start_consuming()
        except KeyboardInterrupt as e:
            channel.stop_consuming()
            self.stdout.write('stopping listening')
        connection.close()
