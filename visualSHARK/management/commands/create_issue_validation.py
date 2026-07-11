#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys

from django.core.management.base import BaseCommand
from visualSHARK.models import Issue, IssueSystem, Project, Commit, VCSSystem
from visualSHARK.models import IssueValidation, IssueValidationUser
from visualSHARK.util.helper import TICKET_TYPE_MAPPING
from django.contrib.auth.models import User

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

        # map issue_ids to their linked commits
        cmap = {}
        commit_qs = Commit.objects.timeout(False).filter(linked_issue_ids__0__exists=True).only('id', 'linked_issue_ids')
        print(f"Total commits with 'linked_issue_ids' found by MongoEngine: {commit_qs.count()}")
        
        for commit in commit_qs:
            for l in commit.linked_issue_ids:
                cmap[l] = commit.id

        print(f"Total mapped issue keys collected in cmap: {len(cmap.keys())}")

        projects = Project.objects.timeout(False).all()
        print(f"Total projects found in MongoEngine: {projects.count()}")

        for project in projects:
            print(f"Processing Project: {project.name} (ID: {project.id})")
            
            issue_systems = IssueSystem.objects.timeout(False).filter(project_id=project.id)
            print(f"Found {issue_systems.count()} IssueSystems for this project.")
            
            for issue_system in issue_systems:
                print(f"Processing IssueSystem ID: {issue_system.id}")
                
                issues = Issue.objects.timeout(False).filter(issue_system_ids=issue_system.id)
                # issues = Issue.objects.timeout(False).filter(__raw__={'issue_system_ids': issue_system.id})
                print(f"Found {issues.count()} raw Issues inside this IssueSystem.")

                if issues.count() == 0:
                    print(f"System {issue_system.id} is empty. Let's inspect raw MongoDB definitions...")
                    try:
                        # Grab the native pymongo client directly from MongoEngine's active connection
                        from mongoengine.connection import get_db
                        raw_mongo = get_db()
                        
                        # Inspect the 'issue' collection globally for ANY sample document
                        sample_issue = raw_mongo['issue'].find_one()
                        
                        if sample_issue:
                            print(f"Real field name for system ID: 'issue_system_id' -> {sample_issue.get('issue_system_id')}")
                            print(f"Real field name for project ID: 'project_id' -> {sample_issue.get('project_id')}")
                            print(f"Available keys in document: {list(sample_issue.keys())}")
                        else:
                            print("The 'issue' collection is completely EMPTY in MongoDB!")
                    except Exception as e:
                        print(f"Debug look up failed: {e}")

                created_in_this_system = 0
                
                for issue in issues:
                    linked = issue.id in cmap.keys()
                    issue_type_unified = ""
                    issue_type = ""
                    if issue.issue_type is not None:
                        issue_type = issue.issue_type

                        issue_type_unified = TICKET_TYPE_MAPPING.get(issue.issue_type.lower().strip())
                        if not issue_type_unified:
                            issue_type_unified = 'other'

                    validation, created = IssueValidation.objects.get_or_create(
                        project_id=project.id,
                        issue_system_id=issue_system.id,
                        issue_id=issue.id,
                        issue_type=issue_type,
                        issue_type_unified=issue_type_unified,
                        linked=linked,
                        resolution=issue.issue_type_verified is not None
                    )
                    validation.save()
                    if created:
                        created_in_this_system += 1
                        
                    for key, value in issue.issue_type_manual.items():
                        validationUser, created = IssueValidationUser.objects.get_or_create(
                            user=User.objects.get(username=key),
                            issue_validation=validation,
                            label=value
                        )
                        validationUser.save()
                
                print(f"Successfully saved {created_in_this_system} new SQL validation rows for this system.")

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))