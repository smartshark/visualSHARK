#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from visualSHARK.models import Hunk, LeaderboardSnapshot


class Command(BaseCommand):
    help = 'Update leaderboard numbers'

    def handle(self, *args, **options):
        board = {}
        for h in Hunk.objects.filter(lines_manual__exists=True):
            for username, lines in h.lines_manual.items():
                if username not in board.keys():
                    board[username] = 0
                board[username] += len(lines)

        ls = LeaderboardSnapshot()
        ls.data = json.dumps(board)
        ls.save()
