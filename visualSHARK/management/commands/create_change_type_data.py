#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from visualSHARK.models import ChangeTypeLabel, Project


class Command(BaseCommand):

    help = 'Create data for the change type labels'

    def handle(self, *args, **options):

        dat = {}
        with open('change_types.pickle', 'rb') as f:
            dat = pickle.load(f)

        count = 0
        for data in dat:
            u1 = User.objects.get(username='atrautsch')
            u2 = User.objects.get(username='erbel')

            p = Project.objects.get(name=data['project'])

            c1 = ChangeTypeLabel(user=u1, project_name=p.name, revision_hash=data['revision_hash'], is_perfective=data['internal_quality'], is_corrective=data['external_quality'])
            c1.save()

            c2 = ChangeTypeLabel(user=u2, project_name=p.name, revision_hash=data['revision_hash'])
            c2.save()

            count += 1

        self.stdout.write(self.style.SUCCESS('[OK]') + ' imported {} change type instances'.format(count))
