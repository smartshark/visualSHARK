#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys

from django.core.management.base import BaseCommand
from visualSHARK.models import Issue, IssueSystem, Project
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

    help = 'Create issue validation objects'


    def handle(self, *args, **options):
        start = timeit.default_timer()

        IssueValidationUser.objects.all().delete()
        IssueValidation.objects.all().delete()

        for project in Project.objects.all():
            for issue_system in IssueSystem.objects.filter(project_id=project.id):
                for issue in Issue.objects.all():
                    linked = len(issue.issue_links) > 0
                    issue_type_unified = ""
                    issue_type = ""
                    if issue.issue_type != None:
                        issue_type = issue.issue_type
                        issue_type_unified = TICKET_TYPE_MAPPING.get(issue.issue_type.lower().strip())
                    validation, created = IssueValidation.objects.get_or_create(
                        project_id=project.id,
                        issue_system_id=issue_system.id,
                        issue_id=issue.id,
                        issue_type=issue_type,
                        issue_type_unified=issue_type_unified,
                        linked=linked,
                        resolution=issue.issue_type_verified != None
                    )
                    validation.save()


        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
