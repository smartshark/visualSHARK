#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date

from django.core.management.base import BaseCommand

from visualSHARK.models import VCSSystem, Commit, Project, File, Issue, MailingList, Message, IssueSystem
from visualSHARK.models import ProjectStats


class Command(BaseCommand):
    help = 'Create Project Stats'

    def handle(self, *args, **options):

        for pro in Project.objects.all():

            ps, created = ProjectStats.objects.get_or_create(project_name=pro.name, stats_date=date.today())

            if created:
                self.stdout.write(self.style.SUCCESS('[OK]') + ' Creating Stats for Project {}'.format(pro.name))
            else:
                self.stdout.write(self.style.SUCCESS('[OK]') + ' Updating Stats for Project {}'.format(pro.name))

            tmp = {'number_commits': 0,
                   'number_issues': 0,
                   'number_files': 0,
                   'number_messages': 0,
                   'number_people': 0}
            people = []

            # vcs / commits
            for vcs in VCSSystem.objects.filter(project_id=pro.id):
                tmp['number_commits'] += Commit.objects.filter(vcs_system_id=vcs.id).count()
                tmp['number_files'] += File.objects.filter(vcs_system_id=vcs.id).count()
                people += Commit.objects.filter(vcs_system_id=vcs.id).distinct('author_id')
                people += Commit.objects.filter(vcs_system_id=vcs.id).distinct('committer_id')

            # issue systems / issues
            for iss in IssueSystem.objects.filter(project_id=pro.id):
                tmp['number_issues'] += Issue.objects.filter(issue_system_id=iss.id).count()
                people += Issue.objects.filter(issue_system_id=iss.id).distinct('creator_id')
                people += Issue.objects.filter(issue_system_id=iss.id).distinct('reporter_id')
                people += Issue.objects.filter(issue_system_id=iss.id).distinct('assignee_id_id')

            # mailinglist / emails
            for ml in MailingList.objects.filter(project_id=pro.id):
                tmp['number_messages'] += Message.objects.filter(mailing_list_id=ml.id).count()
                people += Message.objects.filter(mailing_list_id=ml.id).distinct('from_id')
                for pidlist in Message.objects.filter(mailing_list_id=ml.id).values_list('to_ids'):
                    people += pidlist
                for pidlist in Message.objects.filter(mailing_list_id=ml.id).values_list('cc_ids'):
                    people += pidlist

            unic = list(set(people))
            tmp['number_people'] = len(unic)

            for k, v in tmp.items():
                setattr(ps, k, v)
            ps.save()
