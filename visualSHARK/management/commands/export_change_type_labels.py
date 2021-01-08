#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from visualSHARK.models import ChangeTypeLabel, ChangeTypeLabelDisagreement


class Command(BaseCommand):
    help = 'Export change type labels'

    def handle(self, *args, **options):
        user1 = User.objects.get(username='atrautsch')
        user2 = User.objects.get(username='erbel')

        labels = []
        for c1 in ChangeTypeLabel.objects.filter(user=user1):
            quality_improving = c1.is_perfective
            bug_fixing = c1.is_corrective

            c2 = ChangeTypeLabel.objects.get(project_name=c1.project_name, user=user2, revision_hash=c1.revision_hash)

            # if there is a disagreement fetch the disagreement
            if c1.is_perfective != c2.is_perfective or c1.is_corrective != c2.is_corrective:
                d = ChangeTypeLabelDisagreement.objects.get(project_name=c1.project_name, revision_hash=c1.revision_hash)
                quality_improving = d.is_perfective
                bug_fixing = d.is_corrective

            labels.append({'project_name': c1.project_name, 'revision_hash': c1.revision_hash, 'internal_quality': quality_improving, 'external_quality': bug_fixing})

        with open('change_type_label_export.pickle', 'wb') as f:
            pickle.dump(labels, f)
