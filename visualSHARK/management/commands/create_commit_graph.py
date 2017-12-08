#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import tempfile
import timeit

from django.core.management.base import BaseCommand
from django.core.files import File as DFile

from visualSHARK.models import CommitGraph, VCSSystem, Commit, Project, FileAction, File, Tag

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


class Command(BaseCommand):
    """Builds Graph representation of the commits for a VCS System and calculates positions of the nodes and saves it as JSON for later use in the CommitGraph View"""

    help = 'Create Commit Graphs'

    def add_arguments(self, parser):
        parser.add_argument('project', help='which project')

    def additional_node_data(self, commit):
        data = {'lines_added': 0, 'lines_deleted': 0, 'files_committed': 0, 'java_files_committed': 0, 'python_files_committed': 0, 'files_added': 0, 'files_modified': 0, 'files_renamed': 0, 'files_deleted': 0, 'files_copied': 0, 'is_tag': False}

        if Tag.objects.filter(commit_id=commit.id).count() > 0:
            data['is_tag'] = True

        for fa in FileAction.objects.filter(commit_id=commit.id):
            file = File.objects.get(id=fa.file_id)
            data['files_committed'] += 1
            if file.path.endswith('.java'):
                data['java_files_committed'] += 1
            if file.path.endswith('.py'):
                data['python_files_committed'] += 1
            data['lines_added'] += fa.lines_added
            data['lines_deleted'] += fa.lines_deleted

            if fa.mode.lower() == 'a':
                data['files_added'] += 1
            if fa.mode.lower() == 'm':
                data['files_modified'] += 1
            if fa.mode.lower() == 'r':
                data['files_renamed'] += 1
            if fa.mode.lower() == 'c':
                data['files_copied'] += 1
            if fa.mode.lower() == 'd':
                data['files_deleted'] += 1
        return data

    def create_graphs(self, vcs_id):
        directed_graph = nx.DiGraph()

        nodes = {}
        for c in Commit.objects.timeout(False).filter(vcs_system_id=vcs_id):
            directed_graph.add_node(c.revision_hash)
            nodes[c.revision_hash] = self.additional_node_data(c)

        for c in Commit.objects.timeout(False).filter(vcs_system_id=vcs_id):
            for p in c.parents:
                try:
                    p1 = Commit.objects.get(vcs_system_id=vcs_id, revision_hash=p)
                    directed_graph.add_edge(p1.revision_hash, c.revision_hash)
                except Commit.DoesNotExist:
                    self.stdout.write(self.style.WARNING('[WARN]') + ' Commit: {} is parent of {} but it does not exist! Skipping...'.format(p, c.revision_hash))

        return directed_graph, nodes

    def add_pos(self, nx_graph):
        return graphviz_layout(nx_graph, prog='neato')

    def scale_x(self, x, min_x, max_x):
        x = (x - min_x) / (max_x - min_x)
        x = x * 1000 + 10  # x * scaleFactor + offsetX
        return x

    def scale_y(self, y, min_y, max_y):
        y = (y - min_y) / (max_y - min_y)
        y = y * (1000 / 4 * 3) + 10  # y * scaleFactor (4/3 format) + offsetX
        return y

    def generate_json(self, nx_graph, pos, node_data):
        # find min, max first
        max_x = 0
        max_y = 0
        min_x = float('inf')
        min_y = float('inf')
        for u, v in nx_graph.edges():
            max_x = max(max_x, pos[u][0], pos[v][0])
            max_y = max(max_y, pos[u][1], pos[v][1])
            min_x = min(min_x, pos[u][0], pos[v][0])
            min_y = min(min_y, pos[u][1], pos[v][1])

        # recalculate pos
        nodes = {}
        for k, v in pos.items():
            nodes[k] = {}
            nodes[k].update(**node_data[k])
            nodes[k]['x'] = self.scale_x(v[0], min_x, max_x)
            nodes[k]['y'] = self.scale_y(v[1], min_y, max_y)

        edges = []
        for u, v in nx_graph.edges():
            x1 = self.scale_x(pos[u][0], min_x, max_x)
            x2 = self.scale_x(pos[v][0], min_x, max_x)
            y1 = self.scale_y(pos[u][1], min_y, max_y)
            y2 = self.scale_y(pos[v][1], min_y, max_y)
            edges.append({'key1': u, 'key2': v, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})

        return json.dumps({'nodes': nodes, 'edges': edges, 'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y': max_y})

    def handle(self, *args, **options):
        start = timeit.default_timer()
        project = Project.objects.get(name__iexact=options['project'])
        vcs = VCSSystem.objects.get(project_id=project.id)
        vcs_id = str(vcs.id)
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Creating Commit Graph for Project {} ({})'.format(project.name, vcs_id))

        cg, created = CommitGraph.objects.get_or_create(vcs_system_id=vcs_id)

        # if created:
        cg.title = project.name
        directed_graph, nodes = self.create_graphs(vcs_id)

        directed_pickle_name = '{}_directed.gpickle'.format(project.name.lower())
        directed_pickle_path = os.path.join(tempfile.gettempdir(), directed_pickle_name)
        nx.write_gpickle(directed_graph, directed_pickle_path)
        cg.directed_pickle.save(name=directed_pickle_name, content=DFile(open(directed_pickle_path, 'rb')))

        # calculate node positions with graphvis
        pos = self.add_pos(directed_graph)

        # write json string to file
        directed_json_name = '{}_directed_graph.json'.format(project.name.lower())
        directed_json_path = os.path.join(tempfile.gettempdir(), directed_json_name)
        with open(directed_json_path, 'w') as f:
            f.write(self.generate_json(directed_graph, pos, nodes))

        # safe json file in CommitGraph
        cg.directed_graph.save(name=directed_json_name, content=DFile(open(directed_json_path, 'r')))
        cg.save()
        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))
