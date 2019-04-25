#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import timeit

from django.core.management.base import BaseCommand

from visualSHARK.models import CommitLabelField


class Command(BaseCommand):
    """Fetches schema.json from Labelshark to automatically populate the CommitLabelApproach model."""

    help = 'Fetches commit labeling approaches'

    def handle(self, *args, **options):
        start = timeit.default_timer()

        # 1. fetch schema.json from labelSHARK github
        r = requests.get('https://raw.githubusercontent.com/smartshark/labelSHARK/master/plugin_packaging/schema.json')
        dat = r.json()

        for c in dat['collections']:
            if c['collection_name'] == 'commit':
                for field in c['fields']:
                    if field['field_name'] == 'labels':
                        for f in field['fields']:
                            if 'CommitLabel' in f['logical_type']:
                                tmp = f['field_name'].split('_')
                                approach = tmp[0]
                                name = '_'.join(tmp[1:])
                                CommitLabelField.objects.get_or_create(approach=approach, name=name, description=f['desc'])

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
