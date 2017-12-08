#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys

import networkx as nx
from pprint import pprint as pp

from django.core.management.base import BaseCommand

from visualSHARK.models import VCSSystem, Commit, Project, FileAction, File, Tag, CommitGraph
from visualSHARK.util.helper import tag_filter, OntdekBaan3


log = logging.getLogger()
log.setLevel(logging.DEBUG)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)


class Command(BaseCommand):
    """Creates some git statistics."""

    help = 'Get Git statistics for a project'

    def add_arguments(self, parser):
        parser.add_argument('project', help='which project')

    def get_version_tags(self, vcs_id):
        versions = tag_filter(Tag.objects.filter(vcs_system_id=vcs_id), discard_qualifiers=True, discard_patch=True)

        cg = CommitGraph.objects.get(vcs_system_id=vcs_id)
        dg = nx.read_gpickle(cg.directed_pickle.path)

        import importlib
        approach = 'commit_to_commit'
        mod = importlib.import_module('mynbouSHARK.path_approaches.{}'.format(approach))

        for i, version in enumerate(versions):
            if len(versions) <= i + 1:
                print('end oflist', i)
                continue
            print('{} -> {}'.format(versions[i]['original'], versions[i + 1]['original']))

            # tags without branches from svn->git
            start_commit = versions[i]['revision']
            while not Commit.objects.get(vcs_system_id=vcs_id, revision_hash=start_commit).branches:
                print('start_commit {} has no branches, trying parent'.format(start_commit))
                start_commit = list(dg.pred[start_commit])[0]

            # start_commit = versions[i]['revision']
            end_commit = versions[i + 1]['revision']

            if approach == 'commit_to_commit':
                c = OntdekBaan3(dg)
                for path in c.get_all_paths(start_commit, end_commit):
                    print('path length: {}'.format(len(path)))
                # c = mod.OntdekBaan2(dg)
                # for path in c.get_all_paths(start_commit, end_commit):
                #     print('path length: {}'.format(len(path)))
        return versions

    def create_stats(self, vcs_id):

        commit_authors = set()
        file_authors = {}
        data = {'files_renamed': 0,
                'files_modified': 0,
                'files_copied': 0,
                'files_deleted': 0,
                'files_added': 0,
                'code_files_renamed': 0,
                'code_lines_added': 0,
                'code_lines_deleted': 0,
                'other_lines_added': 0,
                'other_lines_deleted': 0,
                'tags': []
                }
        for c in Commit.objects.filter(vcs_system_id=vcs_id):

            for tag in Tag.objects.filter(commit_id=c.id):
                data['tags'].append(tag.name)

            if c.author_id not in commit_authors:
                commit_authors.add(c.author_id)
            for fa in FileAction.objects.filter(commit_id=c.id):
                f = File.objects.get(id=fa.file_id)

                # file authors
                if fa.file_id not in file_authors.keys():
                    file_authors[fa.file_id] = set()
                    file_authors[fa.file_id].add(c.author_id)
                else:
                    if c.author_id not in file_authors[fa.file_id]:
                        file_authors[fa.file_id].add(c.author_id)

                # lines
                if f.path.endswith('.java') or f.path.endswith('.py'):
                    data['code_lines_added'] += fa.lines_added
                    data['code_lines_deleted'] += fa.lines_deleted
                else:
                    data['other_lines_added'] += fa.lines_added
                    data['other_lines_deleted'] += fa.lines_deleted

                # file operations
                if fa.mode.lower() == 'a':
                    data['files_added'] += 1
                if fa.mode.lower() == 'm':
                    data['files_modified'] += 1
                if fa.mode.lower() == 'r':
                    if f.path.endswith('.java') or f.path.endswith('.py'):
                        data['code_files_renamed'] += 1
                    data['files_renamed'] += 1
                if fa.mode.lower() == 'c':
                    data['files_copied'] += 1
                if fa.mode.lower() == 'd':
                    data['files_deleted'] += 1

        data['avg_authors_per_file'] = 0
        for k, v in file_authors.items():
            data['avg_authors_per_file'] += len(v)

        data['avg_authors_per_file'] /= len(file_authors)
        data['authors'] = len(commit_authors)
        return data

    def handle(self, *args, **options):
        start = timeit.default_timer()

        project = Project.objects.get(name__iexact=options['project'])
        vcs = VCSSystem.objects.get(project_id=project.id)
        vcs_id = str(vcs.id)

        self.stdout.write(self.style.SUCCESS('[OK]') + ' Getting Stats for Project {} ({})'.format(project.name, vcs_id))

        stats = self.create_stats(vcs_id)
        stats['code_lines'] = stats['code_lines_added'] - stats['code_lines_deleted']
        stats['other_lines'] = stats['other_lines_added'] - stats['other_lines_deleted']
        pp(stats)

        ret = self.get_version_tags(vcs_id)
        pp(ret)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
