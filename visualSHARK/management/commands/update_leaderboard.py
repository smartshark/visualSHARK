#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from visualSHARK.models import Hunk, LeaderboardSnapshot, FileAction, Commit, Issue


class Command(BaseCommand):
    help = 'Update leaderboard numbers'

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

        ls = LeaderboardSnapshot()
        ls.data = json.dumps(board)
        ls.save()
