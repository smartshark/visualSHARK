#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from visualSHARK.models import UserProfile


class Command(BaseCommand):
    help = 'Reset open issues'

    def handle(self, *args, **options):
        for up in UserProfile.objects.all():
            print('cleared {} for {}'.format(up.line_label_last_issue_id, up.user.username))
            up.line_label_last_issue_id = ''
            up.save()
