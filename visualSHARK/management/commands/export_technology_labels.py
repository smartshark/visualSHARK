#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from visualSHARK.util.exporter import export_technology_labels


class Command(BaseCommand):
    help = 'Export technology labels'

    def handle(self, *args, **options):
        out = {}
        for user in User.objects.filter(groups__name='technology label'):
            out[user.username] = export_technology_labels(user)

        with open('technology_export.json', 'w') as export_file:
            json.dump(out, export_file)
