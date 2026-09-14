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

    direct_link_jira = re.compile('(?P<ID>([A-Z][A-Z0-9_]+-[0-9]+|#[0-9]+))', re.M)

    def handle(self, *args, **options):
        start = timeit.default_timer()

        for project in Project.objects.all():
            self.perform_heuristic(project.id)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))

    def perform_heuristic(self, project_id):
        vcs_system_id = VCSSystem.objects(project_id=project_id).first()
        processed_count = 0
        matched_count = 0
        for commit in Commit.objects(vcs_system_ids=vcs_system_id).only('id',
                                                                       'revision_hash', 'vcs_system_ids',
                                                                       'linked_issue_ids', 'message',
                                                                       'labels', 'szz_issue_ids'):
            processed_count += 1
            # heuristic only applies to commits that have a single issue link
            if commit.linked_issue_ids and len(commit.linked_issue_ids) == 1:
                issue = Issue.objects(id=commit.linked_issue_ids[0]).get()
                
                # Safe parsing block for the Issue tracking ID string
                try:
                    if "-" in issue.external_id:
                        id_number_issue = int(issue.external_id.split("-")[1])
                    else:
                        # Fallback if the external_id is already an integer sequence string
                        id_number_issue = int(issue.external_id)
                except (ValueError, IndexError, TypeError):
                    id_number_issue = 0
    
                id_number_commit = None
                
                # Parse the commit message for issue references
                for m in self.direct_link_jira.finditer(commit.message.strip()):
                    # if m.start() <= 1:
                    match_in_commit = m.group('ID').upper()
                    try:
                        if "-" in match_in_commit:
                            id_number_commit = int(match_in_commit.split("-")[1])
                        else:
                            # Clean non-numeric characters (like '#') out of the string if present
                            clean_id = ''.join(c for c in match_in_commit if c.isdigit())
                            id_number_commit = int(clean_id) if clean_id else None
                    except (ValueError, IndexError, TypeError):
                        id_number_commit = None

                # Verify if the parsed issue number matches the commit message metadata
                if id_number_commit is not None and id_number_issue == id_number_commit:
                    matched_count += 1
                    commit.fixed_issue_ids = [issue.id]
                    if commit.validations is None:
                        commit.validations = ["issue_links"]
                    else:
                        if "issue_links" not in commit.validations:
                            commit.validations.append("issue_links")
                    # commit.save()
                    Commit.objects(id=commit.id).update_one(
                        set__fixed_issue_ids=[issue.id],
                        set__validations=commit.validations
                    )

        log.info(f"Processed {processed_count} loops. Successfully matched & saved {matched_count} links to DB!")
