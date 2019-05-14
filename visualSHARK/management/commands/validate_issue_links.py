#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys
import re

from django.core.management.base import BaseCommand
from visualSHARK.models import Issue, VCSSystem, Project, Commit

log = logging.getLogger()
log.setLevel(logging.DEBUG)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)


class Command(BaseCommand):

    help = 'Validate the issue links with a heuristic'

    direct_link_jira = re.compile('(?P<ID>[A-Z][A-Z0-9_]+-[0-9]+)', re.M)

    def handle(self, *args, **options):
        start = timeit.default_timer()

        for project in Project.objects.all():
            self.perform_heuristic(project.id)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))

    def perform_heuristic(self, project_id):
        vcs_system_id = VCSSystem.objects(project_id=project_id).get().id
        for commit in Commit.objects(vcs_system_id=vcs_system_id).only('id',
                                                                       'revision_hash', 'vcs_system_id',
                                                                       'linked_issue_ids', 'message',
                                                                       'labels', 'szz_issue_ids'):
            # heuristic only applies to commits that have a single issue link
            if commit.linked_issue_ids and len(commit.linked_issue_ids) == 1:
                issue = Issue.objects(id=commit.linked_issue_ids[0]).get()
                id_number_issue = int(issue.external_id.split("-")[1])
                id_number_commit = None
                # find match to JIRA pattern and determine if it is at the beginning of the commit
                for m in self.direct_link_jira.finditer(commit.message.strip()):
                    if m.start() <= 1:
                        match_in_commit = m.group('ID').upper()
                        id_number_commit = int(match_in_commit.split("-")[1])
                # if there is a JIRA pattern at the beginning of the commit, check if the linked number matches the issue
                # check only for numbers instead of whole external id takes care of typos
                if id_number_commit is not None and id_number_issue == id_number_commit:
                    # if this is the case, the heuristic found a match
                    commit.fixed_issue_ids = [issue.id]
                    if commit.validations is None:
                        commit.validations = ["issue_links"]
                    else:
                        commit.validations.append("issue_links")
                    commit.save()
