# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from visualSHARK.util.rmq import send_to_user


class Command(BaseCommand):
    """Send Message to User."""
    help = 'Send Message to User Topic Channel.'

    def add_arguments(self, parser):
        parser.add_argument('user', help='which user')

    def handle(self, *args, **options):

        u = User.objects.filter(username__iexact=options['user'])
        print('sending to channel: {}'.format(u[0].profile.channel))
        send_to_user(u[0].profile.channel, {'msg': 'test'})