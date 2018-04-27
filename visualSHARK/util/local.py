#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from visualSHARK.models import Commit, CodeEntityState
from visualSHARK.models import VcsHistory


def create_vcs_history(data):
    """Create VCS History for the given vcs_system_id.

    1. select origin/head branch from Branches for the VCS
    2. find shortest path from Branch Tip to first commit (test every commit without parents)
    3. for each commit collect this data
    """
    ret = False
    msg = {}

    if 'vcs_system_id' not in data.keys():
        return ret, msg



    agg = {}
    for c in Commit.objects.filter(vcs_system_id=data['vcs_system_id']).order_by('committer_date'):
        dt = c.committer_date
        utc = datetime.fromtimestamp(c.committer_date.timestamp() + (c.committer_date_offset * 60))
        date = str(utc.date())

        if date not in agg.keys():
            agg[date] = {'num_commits': 0, 'lloc': 0, 'cloc': 0, 'mccc': 0}

        agg[date]['num_commits'] += 1

        # only count last commit if we have multiple commits on this date
        tmp = {'lloc': 0, 'cloc': 0, 'mccc': 0}
        for ces in CodeEntityState.objects.filter(commit_id=c.id, ce_type='file'):
            tmp['lloc'] += ces.metrics['LLOC']
            tmp['cloc'] += ces.metrics['CLOC']
            tmp['mccc'] += ces.metrics['McCC']

        for k in ['lloc', 'cloc', 'mccc']:
            agg[date][k] = tmp[k]

    for k, v in agg.items():
        VcsHistory.objects.create_or_update(v)

    return ret, msg
