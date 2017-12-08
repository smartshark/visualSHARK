#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import timeit

from django.core.management.base import BaseCommand
from django.conf import settings

from visualSHARK.models import Project, VCSSystem


class Command(BaseCommand):
    """Remote access to the ServerSHARK."""

    help = 'Remote access to the ServerSHARK.'

    def add_arguments(self, parser):
        parser.add_argument('project', help='which project')

    def handle(self, *args, **options):
        project = Project.objects.get(name__iexact=options['project'])
        vcs_system = VCSSystem.objects.get(project_id=project.id)

        start = timeit.default_timer()
        # 1. fetch schema.json from labelSHARK github
        r = requests.get('http://127.0.0.1:8001/remote/plugin/?ak={}'.format(settings.API_KEY))
        dat = r.json()

        r = requests.get('http://127.0.0.1:8001/remote/argument/?ak={}&plugin_ids={}'.format(settings.API_KEY, '1,21'))
        arguments = r.json()

        vals = {'path_approach': 'commit_to_commit',
                'defect_label_name': 'adjustedszz_bugfix',
                'metric_approach': 'sum_only',
                'dataset': '1.2',
                'start_commit': '84ce5d6242bf58aa64e8b3ce0187b214d8498c8c',
                'end_commit': '698b22e434ce3c0b03c84c1153a44b002989fb1e',
                'url': '{}'.format(vcs_system.url)}

        # mecoshark
        #vals['execution'] = 'rev'
        #vals['revisions'] = '84ce5d6242bf58aa64e8b3ce0187b214d8498c8c'
        #vals['url'] = '{}'.format(vcs_system.url)

        form_args = []
        for plugin_id, args in arguments.items():
            for arg in args:
                val = vals.get(arg['name'], '')
                if not val:
                    tmp = settings.SUBSTITUTIONS.get(arg['name'], '')
                    if tmp:
                        val = tmp['name']
                form_args.append(('{}_argument_{}'.format(plugin_id, arg['id']), val))

        # plugins
        # - 1. vcsSHARK
        # - 12 mecoSHARK
        # - 13 coastSHARK
        # - 21 mynbouSHARK

        # 2. start new collection for mynbouSHARK

        req = {'ak': settings.API_KEY,
               'plugin_ids': '1,21',
               'project_mongo_ids': '{}'.format(project.id),
               'repository_url': '{}'.format(vcs_system.url),

               # mecoshark
               # 'execution': 'rev',
               # 'revisions': '635da659c0c900b6907d2e07235343d1eb81d605',

               # '21_argument_290': '{}'.format(vcs_system.url),  # repo_url mynbouSHARK
               # '21_argument_298': 'commit_to_commit',  # path_approach
               # '21_argument_299': 'adjustedszz_bugfix',  # defect_label_name
               # '21_argument_300': 'sum_only',  # metric_approach
               # '21_argument_301': '1.3',  # dataset_name (1.2)
               # '21_argument_302': '898dbe87a3783ed3ec2d4e96706eac8e7240119b',  # start_commit
               # '21_argument_303': '3690771806d80a3265071ad4932257d03e4c045f',  # end_commit
               }
        for k, v in form_args:
            req[k] = v

        r = requests.post('http://127.0.0.1:8001/remote/collect/', data=req)

        print(r.status_code)
        print(r.text)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
