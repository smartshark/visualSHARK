#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import io

from datetime import datetime, date

import networkx as nx

from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework import viewsets as rviewsets
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework import filters
import django_filters

from mongoengine.queryset.visitor import Q

from .models import Commit, Project, VCSSystem, IssueSystem, Token, People, FileAction, File, Tag, CodeEntityState, Issue, Message, MailingList, MynbouData
from .models import CommitGraph, CommitLabelField, ProjectStats, VSJob, VSJobType

from .serializers import CommitSerializer, ProjectSerializer, VcsSerializer, IssueSystemSerializer, AuthSerializer, SingleCommitSerializer, FileActionSerializer, TagSerializer, CodeEntityStateSerializer, IssueSerializer, PeopleSerializer, MessageSerializer, SingleIssueSerializer, MailingListSerializer, FileSerializer
from .serializers import CommitGraphSerializer, CommitLabelFieldSerializer, ProductSerializer, SingleMessageSerializer, VSJobSerializer

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel, OneToOneRel

from rest_framework.filters import OrderingFilter

from .util import prediction
from .util.helper import tag_filter, OntdekBaan3 as OntdekBaan

# from visibleSHARK.util.label import LabelPath
# from mynbou.label import LabelPath


class RelatedOrderingFilter(OrderingFilter):
    """Extends OrderingFilter to support ordering by fields in related models."""

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related

        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:

            field = model._meta.get_field(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.rel and len(components) == 2:
                return self.is_valid_field(field.rel.to, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, fields, view):
        return [term for term in fields if self.is_valid_field(queryset.model, term.lstrip('-'))]


class Auth(APIView):
    permission_classes = ()
    schema = None

    def get(self, request):
        username = request.META.get('HTTP_X_USER')
        password = request.META.get('HTTP_X_PASS')

        if not username or not password:
            raise exceptions.AuthenticationFailed()

        user = authenticate(username=username, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed()

        # we just try to avoid ReconnectErrors here
        try:
            _ = Project.objects.count()
        except:
            pass

        token = Token.objects.filter(user=user)
        ass = AuthSerializer(token, many=True)
        tmp = ass.data
        tmp[0]['is_superuser'] = user.is_superuser
        tmp[0]['channel'] = user.profile.channel
        return Response(tmp)


class MongoReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Helper to allow filtering and searching via the ReST API."""

    mongo_search_fields = ()

    def get_queryset(self):
        """Apply requested searches and filters to the queryset."""
        qry = super().get_queryset()

        # detect filtering
        ft = {}
        for ff in self.filter_fields:
            fr = self.request.query_params.get(ff, None)
            if not fr:
                continue
            # date is passed as a string we need to manually reset it here
            if 'date' in ff:
                ft[ff] = datetime.strptime(fr, '%Y-%m-%dT%H:%M:%S')
            else:
                ft[ff] = fr
        qry = qry.filter(**ft)

        # detect searching
        search = self.request.query_params.get('search', None)
        if search:
            q_objects = Q()
            for sf in self.mongo_search_fields:
                # q_objects.add(Q(sf__icontains=search), Q.OR)
                q_objects |= Q(**{'{}__icontains'.format(sf): search})
            qry = qry.filter(q_objects)
        return qry


class TagViewSet(MongoReadOnlyModelViewSet):
    """API Endpoint for Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    ordering_fields = ('name', 'date')
    filter_fields = ('vcs_system_id', 'name')
    mongo_search_fields = ('name',)

    def _inject_data(self, qry):
        ret = []
        for d in qry:
            dat = d.to_mongo()
            dat['commit'] = Commit.objects.get(id=d.commit_id)
            ret.append(dat)
        return ret

    def list(self, request):
        """Nested serializer, we need additional actions for pagination."""
        qry = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qry)
        if page is not None:
            serializer = self.serializer_class(self._inject_data(page), many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(self._inject_data(qry), many=True)
        return Response(serializer.data)


class CommitViewSet(MongoReadOnlyModelViewSet):
    """API Endpoint for Commits."""

    queryset = Commit.objects.all()
    serializer_class = CommitSerializer
    filter_fields = ('revision_hash', 'vcs_system_id', 'committer_date__gte', 'committer_date__lt')
    ordering_fields = ('id', 'revision_hash', 'committer_date')
    mongo_search_fields = ('revision_hash', 'committer_date', 'message')

    def get_queryset(self):
        """Add special case if we search for a person, could be committer or author."""
        qry = super().get_queryset()
        person_id = self.request.query_params.get('person_id', None)
        if person_id:
            qry = qry.filter(Q(author_id=person_id) or Q(committer_id=person_id))
        return qry

    def retrieve(self, request, id=None):
        """Add additional information the each tag."""
        commit = self.queryset.get(revision_hash=id)

        tags = []
        for t in Tag.objects.filter(commit_id=commit.id):
            tags.append({'name': t.name, 'message': t.message})

        issue_links = []
        for li in commit.linked_issue_ids:
            i = Issue.objects.get(id=li)
            issue_links.append({'name': i.external_id, 'id': i.id})

        labels = []
        for l, v in commit.labels.items():
            labels.append({'name': l, 'value': v})

        dat = commit.to_mongo()
        dat['author'] = People.objects.get(id=commit.author_id)
        dat['committer'] = People.objects.get(id=commit.committer_id)
        dat['tags'] = tags
        dat['issue_links'] = issue_links
        dat['labels'] = labels
        serializer = SingleCommitSerializer(dat)
        return Response(serializer.data)


class FileActionViewSet(MongoReadOnlyModelViewSet):
    """API Endpoint for FileActions."""

    queryset = FileAction.objects.all()
    serializer_class = FileActionSerializer
    ordering_fields = ('mode', 'lines_added', 'lines_deleted', 'size_at_commit')
    filter_fields = ('commit_id',)

    def _inject_data(self, qry):
        ret = []
        for d in qry:
            dat = d.to_mongo()
            dat['commit_id'] = d.commit_id
            dat['file'] = File.objects.get(id=d.file_id)
            if d.old_file_id:
                dat['old_file'] = File.objects.get(id=d.old_file_id)
            else:
                dat['old_file'] = None
            ret.append(dat)
        return ret

    def list(self, request):
        """Again a nested serializer."""
        qry = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qry)
        if page is not None:
            serializer = self.serializer_class(self._inject_data(page), many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(self._inject_data(qry), many=True)
        return Response(serializer.data)


class CodeEntityStateViewSet(MongoReadOnlyModelViewSet):
    """API Endpoint for CodeEntityStates."""

    queryset = CodeEntityState.objects.all()
    serializer_class = CodeEntityStateSerializer
    ordering_fields = ('ce_type', 'long_name')
    filter_fields = ('commit_id', 'ce_type', 'long_name')
    mongo_search_fields = ('long_name',)

    def _inject_data(self, qry):
        ret = []
        for d in qry:
            dat = d.to_mongo()
            ret.append(dat)
        return ret

    def list(self, request):
        """Again a nested serializer."""
        qry = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qry)
        if page is not None:
            serializer = self.serializer_class(self._inject_data(page), many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(self._inject_data(qry), many=True)
        return Response(serializer.data)


class FileViewSet(MongoReadOnlyModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    ordering_fields = ('path',)
    filter_fields = ('vcs_system_id', 'path', 'id')
    mongo_search_fields = ('path',)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class VcsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VCSSystem.objects.all()
    serializer_class = VcsSerializer
    filter_fields = ('project_id')


class IssueSystemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IssueSystem.objects.all()
    serializer_class = IssueSystemSerializer
    filter_fields = ('project_id')


class MailingListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer
    filter_fields = ('project_id')


class IssueViewSet(MongoReadOnlyModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    ordering_fields = ('external_id', 'title', 'created_at', 'updated_at', 'status')
    filter_fields = ('issue_system_id', 'external_id', 'title', 'status')
    mongo_search_fields = ('title',)

    def get_queryset(self):
        """Handle special case for person search."""
        qry = super().get_queryset()
        person_id = self.request.query_params.get('person_id', None)
        if person_id:
            qry = qry.filter(Q(creator_id=person_id) | Q(assignee_id=person_id) | Q(reporter_id=person_id))
        return qry

    def retrieve(self, request, id=None):
        """Additional information for GET."""
        r = self.queryset.get(id=id)

        dat = r.to_mongo()
        dat['reporter'] = None
        dat['creator'] = None
        dat['assignee'] = None
        if r.reporter_id:
            dat['reporter'] = People.objects.get(id=r.reporter_id)
        if r.creator_id:
            dat['creator'] = People.objects.get(id=r.creator_id)
        if r.assignee_id:
            dat['assignee'] = People.objects.get(id=r.assignee_id)
        serializer = SingleIssueSerializer(dat)
        return Response(serializer.data)


class PeopleViewSet(MongoReadOnlyModelViewSet):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer
    ordering_fields = ('name', 'username', 'email')
    filter_fields = ('name', 'username', 'email')
    mongo_search_fields = ('name', 'username', 'email')


class MessageViewSet(MongoReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_fields = ('mailing_list_id',)
    ordering_fields = ('subject', 'date')
    mongo_search_fields = ('subject',)

    def get_queryset(self):
        """Handle special case for person search."""
        qry = super().get_queryset()
        person_id = self.request.query_params.get('person_id', None)
        if person_id:
            qry = qry.filter(Q(from_id=person_id))
        return qry

    def retrieve(self, request, id=None):
        """Add additional information the each message."""
        obj = self.queryset.get(id=id)

        recipients = []
        for li in obj.to_ids:
            recipients.append(People.objects.get(id=li))

        cc_ids = []
        for li in obj.cc_ids:
            cc_ids.append(People.objects.get(id=li))

        patches = []
        for li in obj.patches:
            patches.append({'patch': li})

        reference_ids = []
        for li in obj.reference_ids:
            reference_ids.append(Message.objects.get(id=li))

        dat = obj.to_mongo()
        dat['sender'] = None
        dat['in_reply_to_id'] = None
        if obj.in_reply_to_id:
            dat['in_reply_to_id'] = Message.objects.get(id=obj.in_reply_to_id)
        if obj.from_id:
            dat['sender'] = People.objects.get(id=obj.from_id)
        dat['recipients'] = recipients
        dat['reference_ids'] = reference_ids
        dat['cc_ids'] = cc_ids
        dat['patches'] = patches
        serializer = SingleMessageSerializer(dat)
        return Response(serializer.data)


class CommitLabelFieldViewSet(rviewsets.ReadOnlyModelViewSet):
    queryset = CommitLabelField.objects.all()
    serializer_class = CommitLabelFieldSerializer


class CommitGraphViewSet(rviewsets.ReadOnlyModelViewSet):
    """Commit Graph ReST endpoint.

    This endpoint reads the commit graph nodes and their positions (according to graphviz) from the file
    generated during execution of the create_commit_graph command and returns it for the commit graph SVG.
    """

    queryset = CommitGraph.objects.all()
    serializer_class = CommitGraphSerializer
    lookup_field = ('vcs_system_id')
    filter_fields = ('vcs_system_id')

    @detail_route(methods=['get'])
    def mark_nodes(self, request, vcs_system_id=None):
        """Generic node marker.

        We can mark nodes according to search terms or because auf certain (boolan) labels.
        """
        search = request.query_params.get('searchMessage', None)
        label = request.query_params.get('label', None)

        response = {}

        if label:
            labelfield = CommitLabelField.objects.get(pk=label)
            label_name = '{}_{}'.format(labelfield.approach, labelfield.name)

            dat = {'vcs_system_id': vcs_system_id,
                   'labels__{}'.format(label_name): True}
            for v in Commit.objects.filter(**dat):
                response[v.revision_hash] = [label_name]

        if search:
            for v in Commit.objects.filter(vcs_system_id=vcs_system_id, message__icontains=search):
                if v.revision_hash in response.keys():
                    response[v.revision_hash].append('search')
                else:
                    response[v.revision_hash] = ['search']

            for v in Commit.objects.filter(vcs_system_id=vcs_system_id, revision_hash__icontains=search):
                if v.revision_hash in response.keys():
                    response[v.revision_hash].append('search')
                else:
                    response[v.revision_hash] = ['search']

        return Response({'results': response})

    @detail_route(methods=['get'])
    def articulation_points(self, request, vcs_system_id=None):
        """Return list of nodes that are articulation points."""
        cg = CommitGraph.objects.get(vcs_system_id=vcs_system_id)
        dg = nx.read_gpickle(cg.directed_pickle.path)

        mark = nx.articulation_points(dg.to_undirected())

        return Response({'results': mark})

    @detail_route(methods=['get'])
    def product_path(self, request, vcs_system_id=None):
        """Return path for the approach used in this exact product."""
        cg = CommitGraph.objects.get(vcs_system_id=vcs_system_id)

        product_id = request.query_params.get('product_id', None)

        if not product_id:
            raise Exception('need commits')

        p = MynbouData.objects.get(id=product_id)

        # extract approach, start and end commit
        tmp = json.loads(p.file.read())

        dg = nx.read_gpickle(cg.directed_pickle.path)
        approach = tmp['label_path_approach']
        start_commit = tmp['start_commit']
        end_commit = tmp['end_commit']

        nodes = set()
        # import importlib
        # mod = importlib.import_module('mynbouSHARK.path_approaches.{}'.format(approach))
        if approach == 'commit_to_commit':
            c = OntdekBaan(dg)
            for path in c.get_all_paths(start_commit, end_commit):
                nodes = nodes.union(set(path))

        return Response({'paths': [list(nodes)], 'products': [p.name]})

    @detail_route(methods=['get'])
    def path(self, request, vcs_system_id=None):
        cg = CommitGraph.objects.get(vcs_system_id=vcs_system_id)

        start_commit = request.query_params.get('start_commit', None)
        end_commit = request.query_params.get('end_commit', None)

        if not start_commit or not end_commit:
            raise Exception('need commits')

        dg = nx.read_gpickle(cg.directed_pickle.path)

        nodes = set()

        o = OntdekBaan(dg)
        paths = []
        for p in o.get_all_paths(start_commit, end_commit):
            paths.append(p)
            # nodes = nodes.union(set(p))
        # path = nx.shortest_path(dg, start_commit, end_commit)
        # nodes = set(path)

        return Response({'paths': paths})


class ProductViewSet(MongoReadOnlyModelViewSet):
    """Product data from mynbouSHARK."""
    queryset = MynbouData.objects.all()
    serializer_class = ProductSerializer
    filter_fields = ('vcs_system_id',)
    ordering_fields = ('name',)

    @detail_route(methods=['get'])
    def file(self, request, id=None):
        version = MynbouData.objects.get(id=id)
        return Response(json.loads(version.file.read()))

    @detail_route(methods=['get'])
    def file_download(self, request, id=None):
        version = MynbouData.objects.get(id=id)
        f = io.BytesIO(version.file.read())
        response = HttpResponse(f, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="{}.json"'.format(version.name)
        return response


class PredictionEvaluationView(APIView):

    def get(self, request):
        training = request.query_params.get('training', None)
        test = request.query_params.get('test', None)
        model = request.query_params.get('model', None)

        # 1. load files
        train = []
        te = []
        for train_id in training.split(','):
            train.append(json.loads(MynbouData.objects.get(id=train_id).file.read()))

        for test_id in test.split(','):
            te.append(json.loads(MynbouData.objects.get(id=test_id).file.read()))

        # 2. build model & evaluate
        pred = prediction.predict_evaluate(train, te, model)

        return Response(pred)


class PredictionView(APIView):

    def get(self, request):
        training = request.query_params.get('training', None)
        test = request.query_params.get('test', None)
        model = request.query_params.get('model', None)

        # 1. load files
        train = []
        te = []
        for train_id in training.split(','):
            train.append(json.loads(MynbouData.objects.get(id=train_id).file.read()))

        for test_id in test.split(','):
            te.append(json.loads(MynbouData.objects.get(id=test_id).file.read()))

        # 2. build model & predict
        pred = prediction.predict(train, te, model)

        return Response(pred)


class StatsView(APIView):
    # TODO: update to serializer

    def get(self, request):
        projects = {}
        for pro in ProjectStats.objects.filter(stats_date=date.today()):
            projects[pro.project_name] = {
                'commits': pro.number_commits,
                'issues': pro.number_issues,
                'files': pro.number_files,
                'messages': pro.number_messages,
                'people': pro.number_people}
        return Response(projects)


class StatsHistoryView(APIView):
    # TODO: update to serializer

    def get(self, request):
        history = []
        for pro in ProjectStats.objects.values('stats_date').distinct().order_by('stats_date'):
            tmp = {'date': pro['stats_date'], 'commits': 0, 'issues': 0, 'files': 0, 'messages': 0, 'people': 0}
            for p in ProjectStats.objects.filter(stats_date=pro['stats_date']):
                tmp['commits'] += p.number_commits
                tmp['issues'] += p.number_issues
                tmp['files'] += p.number_files
                tmp['messages'] += p.number_messages
                tmp['people'] += p.number_people
            history.append(tmp)
        return Response(history)


class ReleaseView(APIView):

    def get(self, request):
        vcs_system_id = request.GET.get('vcs_system_id', None)
        discard_qualifiers = request.GET.get('discard_qualifiers', True)
        discard_patch = request.GET.get('discard_patch', True)

        discard_qualifiers = discard_qualifiers == 'true'
        discard_patch = discard_patch == 'true'

        versions = tag_filter(Tag.objects.filter(vcs_system_id=vcs_system_id), discard_qualifiers=discard_qualifiers, discard_patch=discard_patch)
        history = {'count': len(versions), 'results': versions}
        # print(history)
        return Response(history)


class VSJobViewSet(rviewsets.ModelViewSet):
    """Job information."""

    queryset = VSJob.objects.all()
    serializer_class = VSJobSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('job_type__name',)
    ordering_fields = ('job_type', 'created_at', 'executed_at', 'error_count')
    search_fields = ('job_type__name',)

    def get_queryset(self):
        qry = super().get_queryset()
        return qry.filter(requested_by=self.request.user)

    @detail_route(methods=['post'])
    def requeue(self, request, pk=None):
        j = VSJob.objects.get(pk=pk)
        j.requeue()

        return HttpResponse(status=202)

    @list_route(methods=['post'])
    def collect_other(self, request, pk=None):
        dat = request.data
        dat['api_url'] = settings.SERVERSHARK_API_URL
        dat['api_key'] = settings.API_KEY
        dat['substitutions'] = settings.SUBSTITUTIONS

        jt = VSJobType.objects.get(ident='collect_other')
        j = VSJob(job_type=jt, requested_by=request.user)
        j.data = json.dumps(dat)
        j.save()

        return HttpResponse(status=202)

    @list_route(methods=['post'])
    def collect_revision(self, request, pk=None):

        # enrich with our data
        dat = request.data
        dat['api_url'] = settings.SERVERSHARK_API_URL
        dat['api_key'] = settings.API_KEY
        dat['substitutions'] = settings.SUBSTITUTIONS

        jt = VSJobType.objects.get(ident='collect_revision')
        j = VSJob(job_type=jt, requested_by=request.user)
        j.data = json.dumps(dat)
        j.save()

        return HttpResponse(status=202)

    @list_route(methods=['post'])
    def test_connection_servershark(self, request, pk=None):

        dat = request.data
        dat['api_url'] = settings.SERVERSHARK_API_URL
        dat['api_key'] = settings.API_KEY
        dat['substitutions'] = settings.SUBSTITUTIONS

        jt = VSJobType.objects.get(ident='test_connection_servershark')
        j = VSJob(job_type=jt, requested_by=request.user)
        j.data = json.dumps(dat)
        j.save()

        print(dat)

        return HttpResponse(status=202)

    @list_route(methods=['post'])
    def test_connection_worker(self, request, pk=None):
        dat = request.data
        jt = VSJobType.objects.get(ident='test_connection_worker')
        j = VSJob(job_type=jt, requested_by=request.user)
        j.data = json.dumps(dat)
        j.save()

        print(dat)

        return HttpResponse(status=202)
