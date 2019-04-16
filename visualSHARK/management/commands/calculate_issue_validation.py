#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys

from django.core.management.base import BaseCommand
from visualSHARK.models import Issue, IssueSystem, Project, Event
from visualSHARK.models import IssueValidation, IssueValidationUser
from visualSHARK.util.helper import TICKET_TYPE_MAPPING

log = logging.getLogger()
log.setLevel(logging.DEBUG)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)


class Command(BaseCommand):

    help = 'Resolve the issue validation objects and save them to the mongodb'

    n = 3

    def handle(self, *args, **options):
        start = timeit.default_timer()

        for issueValidation in IssueValidation.objects.all():
            labeling_count = IssueValidationUser.objects.filter(issue_validation=issueValidation).count()
            if labeling_count > self.n:
                all_same = True
                label = None
                for issueUserValidation in IssueValidationUser.objects.filter(issue_validation=issueValidation):
                    if label == None:
                        label = issueUserValidation.label
                    if issueUserValidation.label != label:
                        all_same = False

                if all_same:
                    issue_db = Issue.objects.get(id=issueValidation.issue_id)
                    issue_db.issue_type_verified = label
                    issue_db.save()

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
