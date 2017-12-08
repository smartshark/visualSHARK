#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import math
import networkx as nx
import logging
import timeit
from collections import deque

from visualSHARK.models import Commit


def tag_filter(tags, discard_qualifiers=True, discard_patch=False):
    versions = []

    # qualifiers are expected at the end of the tag and they may have a number attached
    # it is very important for the b to be at the end otherwise beta would already be matched!
    qualifiers = ['rc', 'alpha', 'beta', 'b']

    # separators are expected to divide 2 or more numbers
    separators = ['.', '_', '-']

    for t in tags:

        tag = t.name
        c = Commit.objects.get(id=t.commit_id)

        qualifier = ''
        remove_qualifier = ''
        for q in qualifiers:
            if q in tag.lower():
                tmp = tag.lower().split(q)
                if tmp[-1].isnumeric():
                    qualifier = [q, tmp[-1]]
                    remove_qualifier = ''.join(qualifier)
                    break
                else:
                    qualifier = [q]
                    remove_qualifier = q
                    break

        # if we have a qualifier we remove it before we check for best number seperator
        tmp = tag.lower()
        if qualifier:
            tmp = tmp.split(remove_qualifier)[0]

        # we only want numbers and separators
        version = re.sub('[a-z]', '', tmp)

        # the best separator is the one separating the most numbers
        best = -1
        best_sep = None
        for sep in separators:
            current = 0
            for v in version.split(sep):
                v = ''.join(c for c in v if c.isdigit())
                if v.isnumeric():
                    current += 1

            if current > best:
                best = current
                best_sep = sep

        version = version.split(best_sep)
        final_version = []
        for v in version:
            v = ''.join(c for c in v if c.isdigit())
            if v.isnumeric():
                final_version.append(int(v))

        # if we have a version we append it to our list
        if final_version:

            # force semver because we are sorting
            if len(final_version) == 1:
                final_version.append(0)
            if len(final_version) == 2:
                final_version.append(0)

            fversion = {'version': final_version, 'original': tag, 'revision': c.revision_hash}
            if qualifier:
                fversion['qualifier'] = qualifier

            versions.append(fversion)

    # discard fliers
    p_version = [int(v['version'][0]) for v in versions]
    sort = sorted(p_version)
    a = 0.25 * len(sort)
    b = 0.75 * len(sort)
    if a.is_integer():
        a = int(a)  # otherwise could be 6.0
        x_025 = ((sort[a] + sort[a + 1]) / 2)
    else:
        x_025 = sort[math.floor(a) + 1]

    if b.is_integer():
        b = int(b)
        x_075 = ((sort[b] + sort[b + 1]) / 2)
    else:
        x_075 = sort[math.floor(b) + 1]

    iqr = x_075 - x_025
    flyer_lim = 1.5 * iqr

    ret = []
    for version in versions:
        major = int(version['version'][0])

        # no fliers in final list
        if major > (x_075 + flyer_lim) or major < (x_025 - flyer_lim):
            print('exclude: {} because {} is not between {} and {}'.format(version['version'], major, (x_025 - flyer_lim), (x_075 + flyer_lim)))
            continue

        if discard_qualifiers and 'qualifier' in version.keys():
            continue

        ret.append(version)

    # sort remaining
    s = sorted(ret, key=lambda x: (x['version'][0], x['version'][1], x['version'][2]))

    ret = []
    for v in s:
        # only minor, we discard patch releases (3rd in semver, everything after 2nd in other schemas)
        if discard_patch:
            if len(v['version']) > 2:
                del v['version'][2:]

        if v['version'] not in [v2['version'] for v2 in ret]:
            ret.append(v)

    return ret


class OntdekBaan3(object):
    """Discover all paths in a commitgraph represented as an NetworkX DAG.

    The Problem:
    High number of paths without repeated nodes (simple paths) in normal Git Workflow.

    The Solution:
    We reset the start node if we have no path to travel to the end node (happens for SVN -> Git Tags).
    We prune the graph to the subgraph containing only paths from our start to end.
    We compute the longest path (which is possible in polynomial time as we work on a DAG).
    We then find all nodes nod already contained in the longest path.
    For each of those nodes we find a connection to a node in the longest path which is a merge or split (because then it is cached in Volg).
    """

    def __init__(self, g):
        self._graph = g.copy()
        self._nodes = set()
        self._log = logging.getLogger(self.__class__.__name__)

    def _prune_graph(self, start, end):
        non_pruned = self._graph.copy()
        for n in non_pruned:
            if not nx.has_path(non_pruned, n, end):
                if n in self._graph:
                    self._graph.remove_node(n)
            if not nx.has_path(non_pruned, start, n):
                if n in self._graph:
                    self._graph.remove_node(n)

    def _find_parent_in_paths(self, node):
        succ = deque(list(self._graph.pred[node]))
        while succ:
            # pop out at the right
            n = succ.pop()
            if n in self._nodes and (len(self._graph.pred[n]) > 1 or len(self._graph.succ[n]) > 1):
                return n

            # append new parents to the left
            for p in self._graph.pred[n]:
                succ.appendleft(p)

    def _find_child_in_paths(self, node):
        succ = deque(list(self._graph.succ[node]))
        while succ:
            # pop out at the right
            n = succ.pop()
            if n in self._nodes and (len(self._graph.pred[n]) > 1 or len(self._graph.succ[n]) > 1):
                return n

            # append new childs to the left
            for s in self._graph.succ[n]:
                succ.appendleft(s)

    def _reset_start_node(self, start, end):
        self._new_start_node = start
        while not nx.has_path(self._graph, self._new_start_node, end):
            self._log.info('no path from {} to {} traveling backwards'.format(self._new_start_node, end))
            parents = list(self._graph.pred[self._new_start_node])
            if len(parents) == 0:
                raise Exception('can not travel backwards from start {}, no parents on {}: ({})!'.format(start, self._new_start_node, parents))
            elif len(parents) > 1:
                # if we have multiple parents, chose the one which has the shortest path to target in undirected graph
                length = len(self._graph)
                chosen_parent = None
                un = self._graph.to_undirected()
                for p in parents:
                    path = nx.shortest_path(un, p, end)
                    if len(path) < length:
                        length = len(path)
                        chosen_parent = p
            else:
                chosen_parent = parents[0]
            self._new_start_node = chosen_parent

        # do we need to reattach our real start node?
        # it could lead to errors if the direction is reversed because Volg does not support the reversed direction
        if self._new_start_node != start:
            self._log.info('real start was {} but we travelled backwards to {}'.format(start, self._new_start_node))
        return self._new_start_node

    def get_all_paths(self, start, end):
        # travel backwards / forwards for unreachable nodes
        new_start = self._reset_start_node(start, end)

        # prune graph to our required sub-graph
        self._prune_graph(new_start, end)

        # start / end can be pre- / appended the same as other nodes not in the longest path
        lp = nx.dag_longest_path(self._graph)

        # we need to ensure that start and end node are at the appropriate
        # if this is raised we could find shortest path from start to lp and end to lp and pre- or append them
        if lp[0] != self._new_start_node or lp[-1] != end:
            raise Exception('start: {} or end {} not in first path!'.format(self._new_start_node, end))

        self._nodes = set(lp)
        yield lp

        for n in self._graph:
            if n not in self._nodes:
                # find parent in lp
                # find child in lp
                p = self._find_parent_in_paths(n)
                c = self._find_child_in_paths(n)

                p1 = nx.shortest_path(self._graph, p, n)
                p2 = nx.shortest_path(self._graph, n, c)

                self._nodes.update(set(p1 + p2))
                yield(p1[:-1] + p2)  # n is in both paths so we cut one of


class OntdekBaan2(object):
    """Discover all paths in a commitgraph represented as an NetworkX DAG.

    The Problem:
    High number of paths without repeated nodes in normal Git Workflow.

    The Solution:
    Split paths at articulation points to reduce number of paths.

    Problem still remaining:
    - no common suffixes are cleared, without Volg caching there may be a problem
    - long running branches that are merged back into master later
    - release branches (because we are taking a lot of information from master)
    """

    def __init__(self, graph):
        self._log = logging.getLogger(self.__class__.__name__)
        self._graph = graph.copy()

    def _preprocess(self, start_node, end_node):
        self._start_node = start_node
        self._end_node = end_node

        self._log.info('finding all paths between {} and {}'.format(start_node, end_node))
        # we need to prune the graph beforehand, this is expensive but otherwise we would have even more paths
        # we also prune common prefix in the implementation, common suffix can only be done later
        st = timeit.default_timer()
        self._log.info('pruning graph')
        non_pruned = self._graph.copy()
        for node in non_pruned:
            for child in iter(non_pruned.succ[node]):
                try:
                    nx.shortest_path(self._graph, child, self._end_node)
                except nx.NetworkXNoPath:
                    self._graph.remove_edge(node, child)

        t = timeit.default_timer() - st
        self._log.info('pruning finished in {:.3f}'.format(t))

        # if our start node contains no path to the end node travel backwards until it does,
        # except if it has more than one parent, then its over and we bail
        self._new_start_node = start_node
        while not nx.has_path(non_pruned, self._new_start_node, end_node):
            self._log.info('no path from {} to {} traveling backwards'.format(self._new_start_node, end_node))
            parents = list(non_pruned.pred[self._new_start_node])
            if len(parents) == 0:
                raise Exception('can not travel backwards from start {}, no parents on {}: ({})!'.format(self._start_node, self._new_start_node, parents))
            elif len(parents) > 1:
                # if we have multiple parents, chose the one which has the shortest path to target in undirected graph
                length = len(non_pruned)
                chosen_parent = None
                un = non_pruned.to_undirected()
                for p in parents:
                    path = nx.shortest_path(un, p, end_node)
                    if len(path) < length:
                        length = len(path)
                        chosen_parent = p
            else:
                chosen_parent = parents[0]
            self._new_start_node = chosen_parent

        # get list of APs
        self._aps = list(nx.articulation_points(self._graph.to_undirected()))

    def get_all_paths(self, start_node, end_node):
        """Return every traversable path between start and end commit."""
        self._preprocess(start_node, end_node)

        ap = self._new_start_node
        full_paths = []
        while ap:
            ap, paths = self._get_paths(ap, self._end_node)

            # we can do this here because it does not matter in which order we traverse the graph
            # we do not need full paths everywhere because of the caching in Volg
            if not full_paths:
                full_paths = paths
                self._log.debug('non ap, assigning full_paths')
            else:
                self._log.debug('encountered AP {} splitting path'.format(ap))  # this is potentially happening quiet often
                # first one gets the complete path, as we do not prune common suffixes
                # we know that the AP (our new starting node) has to be the last element of every path
                # therefore, we chose the first
                full_paths[0] += paths[0][1:]
                full_paths += paths[1:]

        # do we need to reattach our real start node?
        # it could lead to errors if the direction is reversed because Volg does not support the reversed direction
        if self._new_start_node != self._start_node:
            self._log.info('real start was {} but we travelled backwards to {}'.format(self._start_node, self._new_start_node))

        return full_paths

    def _get_paths(self, start_node, end_node):
        """Get all paths where the end_node is reachable or up to an AP."""
        nodes = [start_node]
        paths = [[start_node]]

        # print('{}, {}'.format(nodes, paths))
        new_start = None
        while nodes:
            node = nodes.pop()
            childs = list(self._graph.succ[node])

            # we bail on AP or end_node reached
            if node in self._aps and node != start_node:
                childs = []
                new_start = node

            elif node == end_node:
                childs = []

            # print('node {} childs {}'.format(node, childs))
            if childs:
                nodes += childs

                npath = None
                for path in paths:
                    if path[-1] == node:
                        # by creating a new list instead of copying we eleminate common prefixes in the resulting paths
                        npath = [node]
                        path.append(childs[0])
                        # print('[1] append {} to path {}'.format(childs[0], path))

                # first one we have already
                for child in childs[1:]:
                    # do we already have a path?
                    if npath:
                        path = npath.copy()  # we need this copy here in case of childs > 2
                        path.append(child)
                        paths.append(path)
                        # print('[2] append {} to new path {}'.format(child, npath))

            # this is just for the end node
            if not childs:
                for path in paths:
                    if path[-1] in self._graph.pred[node]:
                        # print('[n] append {} to {} because {}'.format(node, path, path[-1]))
                        path.append(node)
        return new_start, paths
