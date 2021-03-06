#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from visualSHARK.models import CorrectionIssue, Issue, IssueSystem, Project


class Command(BaseCommand):

    help = 'Create issue correction objects for the line label study'

    def handle(self, *args, **options):

        # load pickle
        dat = {}
        with open('correct_required.pickle', 'rb') as f:
            dat = pickle.load(f)

        count = 0
        for user, issue_ids in dat.items():
            username = user
            # 1. get django user for username
            try:
                u = User.objects.get(username=username)
            except User.DoesNotExist:
                raise Exception('user', user, 'does not exist, skipping')

            # 2. get issue and project name for id
            for issue_id in issue_ids:
                i = Issue.objects.get(id=issue_id)

                its = IssueSystem.objects.get(id=i.issue_system_id)
                p = Project.objects.get(id=its.project_id)

                count += 1

                try:
                    ci = CorrectionIssue.objects.get(user=u, external_id=i.external_id, project_name=p.name)
                except CorrectionIssue.DoesNotExist:
                    ci = CorrectionIssue(user=u, external_id=i.external_id, project_name=p.name)
                    ci.save()

        self.stdout.write(self.style.SUCCESS('[OK]') + ' imported {} corrections'.format(count))
