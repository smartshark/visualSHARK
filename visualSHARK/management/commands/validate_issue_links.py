#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys
import re

from django.core.management.base import BaseCommand
from mongoengine.fields import ListField, ObjectIdField
from visualSHARK.models import Issue, VCSSystem, Project, Commit

log = logging.getLogger()
log.setLevel(logging.DEBUG)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)

# if 'vcs_system_ids' not in Commit._fields:
#     Commit._fields['vcs_system_ids'] = ListField(ObjectIdField(), db_field='vcs_system_ids', default=list)
#     Commit._db_field_map['vcs_system_ids'] = 'vcs_system_ids'

class Command(BaseCommand):

    help = 'Validate the issue links with a heuristic'

    # direct_link_jira = re.compile('(?P<ID>[A-Z][A-Z0-9_]+-[0-9]+)', re.M)
    direct_link_jira = re.compile('(?P<ID>([A-Z][A-Z0-9_]+-[0-9]+|#[0-9]+|[0-9]+))', re.M)

    def handle(self, *args, **options):
        start = timeit.default_timer()

        for project in Project.objects.all():
            self.perform_heuristic(project.id)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))

    def perform_heuristic(self, project_id):
        print(f"Running perform_heuristic for Project ID: {project_id}")

        # Bypass the model lookup mismatch and find all commits with links directly
        commits_query = Commit.objects.timeout(False).filter(
            __raw__={
                'linked_issue_ids.0': {'$exists': True}
            }
        # ).only('id', 'revision_hash', 'vcs_system_ids', 'linked_issue_ids', 'message', 'labels', 'szz_issue_ids')
        ).only('id', 'revision_hash', 'vcs_system_id', 'linked_issue_ids', 'message', 'labels', 'szz_issue_ids')

        print(f"Found {commits_query.count()} raw commits with active issue associations.")

        processed_count = 0
        matched_count = 0

        for commit in commits_query:
            processed_count += 1
            
            # The heuristic logic by design only evaluates commits that have exactly 1 link
            if commit.linked_issue_ids and len(commit.linked_issue_ids) == 1:
                try:
                    issue = Issue.objects(id=commit.linked_issue_ids[0]).get()
                except Exception:
                    # Skip cleanly if the referenced issue object does not exist in the database
                    continue

                # print(f"Commit Message: '{commit.message.strip()}'")
                # print(f"Linked Issue External ID: '{issue.external_id}'")
                
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

        print(f"Processed {processed_count} loops. Successfully matched & saved {matched_count} links to DB!")
