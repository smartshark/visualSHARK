#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from visualSHARK.models import Hunk, LeaderboardSnapshot, FileAction, Commit, Issue, Project, IssueSystem


class Command(BaseCommand):
    help = 'Update leaderboard numbers'

    def _projects(self):
        # 0. only validated projects
        PROJECTS = ['ant-ivy', 'archiva', 'calcite', 'cayenne', 'commons-bcel', 'commons-beanutils',
                    'commons-codec', 'commons-collections', 'commons-compress', 'commons-configuration',
                    'commons-dbcp', 'commons-digester', 'commons-io', 'commons-jcs', 'commons-jexl',
                    'commons-lang', 'commons-math', 'commons-net', 'commons-scxml',
                    'commons-validator', 'commons-vfs', 'deltaspike', 'eagle', 'giraph', 'gora', 'jspwiki',
                    'knox', 'kylin', 'lens', 'mahout', 'manifoldcf', 'nutch', 'opennlp', 'parquet-mr',
                    'santuario-java', 'systemml', 'tika', 'wss4j']
        projects = {}
        for project_name in PROJECTS:

            if project_name not in projects:
                projects[project_name] = {'need_issues': set(), 'need_commits': 0, 'issues': {}, 'partial': 0, 'finished': 0, 'partial_1': 0, 'partial_2': 0, 'partial_3': 0}
            p = Project.objects.get(name=project_name)
            its = IssueSystem.objects.get(project_id=p.id)

            # 1. verified bug issues
            for i in Issue.objects.filter(issue_system_id=its.id, issue_type_verified='bug'):

                # 2. only linked ids
                if Commit.objects.filter(fixed_issue_ids=i.id).count() == 0:
                    continue

                projects[project_name]['issues'][i.external_id] = set()

                for c in Commit.objects.filter(fixed_issue_ids=i.id).only('id'):
                    projects[project_name]['need_commits'] += 1

                    for fa in FileAction.objects.filter(commit_id=c.id).only('id'):
                        for h in Hunk.objects.filter(file_action_id=fa.id):
                            projects[project_name]['need_issues'].add(str(i.id))
                            for username, lines in h.lines_manual.items():
                                projects[project_name]['issues'][i.external_id].add(username)
                labels = len(projects[project_name]['issues'][i.external_id])
                if labels > 0 and labels < 4:
                    projects[project_name]['partial'] += 1

                    # add additional information about how many users labeled partially (added 2020-07-06)
                    if labels == 1:
                        projects[project_name]['partial_1'] += 1
                    elif labels == 2:
                        projects[project_name]['partial_2'] += 1
                    elif labels == 3:
                        projects[project_name]['partial_3'] += 1
                if labels >= 4:
                    projects[project_name]['finished'] += 1
            projects[project_name]['need_issues'] = len(projects[project_name]['need_issues'])
        return projects

    def handle(self, *args, **options):
        board = {}
        hunks = {}
        for h in Hunk.objects.filter(lines_manual__exists=True):
            for username, lines in h.lines_manual.items():
                if username not in board.keys():
                    board[username] = {'lines': 0, 'issues': set(), 'commits': set(), 'files': set(), 'projects': set()}
                    hunks[username] = set()
                hunks[username].add(h)
                for label, line_numbers in lines.items():
                    board[username]['lines'] += len(line_numbers)

        # this is kind of inefficient but we do not get to issues from hunks as commit
        # can be linked to more than one issue in fixed_issue_ids
        for i in Issue.objects.filter(issue_type_verified='bug'):
            commits = Commit.objects.filter(fixed_issue_ids=i.id).only('id', 'parents')
            if len(commits) > 0:
                for c in commits:
                    if c.parents:
                        fas = FileAction.objects.filter(commit_id=c.id, parent_revision_hash=c.parents[0])
                    else:
                        fas = FileAction.objects.filter(commit_id=c.id)
                    for fa in fas:
                        for h in Hunk.objects.filter(file_action_id=fa.id, lines_manual__exists=True):
                            for username, lines in h.lines_manual.items():
                                board[username]['issues'].add(str(i.id))
                                board[username]['projects'].add(str(c.vcs_system_id))

        # other counts outside of hunk lines
        for username, hunks in hunks.items():
            for hunk in hunks:
                fa = FileAction.objects.get(id=hunk.file_action_id)
                c = Commit.objects.get(id=fa.commit_id)
                board[username]['commits'].add(str(c.id))
                board[username]['files'].add(str(fa.id))

        # count objects now
        for username, values in board.items():
            board[username]['commits'] = len(values['commits'])
            board[username]['files'] = len(values['files'])
            board[username]['issues'] = len(values['issues'])
            board[username]['projects'] = len(values['projects'])

        # only certain data allowed
        projects = self._projects()
        tosave = {}
        for project_name, values in projects.items():
            tosave[project_name] = {'need_issues': values['need_issues'], 'partial': values['partial'], 'finished': values['finished'], 'partial_1': values['partial_1'], 'partial_2': values['partial_2'], 'partial_3': values['partial_3']}

        ls = LeaderboardSnapshot()
        ls.data = json.dumps({'users': board, 'projects': tosave})
        ls.save()
