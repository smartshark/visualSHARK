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
                    board[username] = {'lines': 0, 'commits': set(), 'files': set()}
                    hunks[username] = set()
                hunks[username].add(h)
                for label, line_numbers in lines.items():
                    board[username]['lines'] += len(line_numbers)

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

        ls = LeaderboardSnapshot()
        ls.data = json.dumps(board)
        ls.save()
