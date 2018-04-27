#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from rest_framework_mongoengine import routers
from rest_framework import routers as rrouters
from rest_framework.documentation import include_docs_urls

from .views import Auth, StatsView

from .views import CommitViewSet, ProjectViewSet, VcsViewSet, IssueSystemViewSet, FileActionViewSet, TagViewSet, CodeEntityStateViewSet, MessageViewSet, PeopleViewSet, IssueViewSet, MailingListViewSet, FileViewSet, ProductViewSet, BranchViewSet
from .views import CommitGraphViewSet, StatsHistoryView, CommitLabelFieldViewSet, PredictionEvaluationView, PredictionView, VSJobViewSet, ReleaseView

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'commit', CommitViewSet)
router.register(r'tag', TagViewSet)
router.register(r'project', ProjectViewSet)
router.register(r'vcs', VcsViewSet)
router.register(r'branch', BranchViewSet)
router.register(r'is', IssueSystemViewSet)
router.register(r'ml', MailingListViewSet)
router.register(r'issue', IssueViewSet)
router.register(r'message', MessageViewSet)
router.register(r'people', PeopleViewSet)
router.register(r'fileaction', FileActionViewSet)
router.register(r'codeentitystate', CodeEntityStateViewSet)
router.register(r'file', FileViewSet)
router.register(r'product', ProductViewSet)

rrouter = rrouters.DefaultRouter()
rrouter.register(r'commitgraph', CommitGraphViewSet)
rrouter.register(r'commitlabel', CommitLabelFieldViewSet)

arouter = rrouters.DefaultRouter()
arouter.register(r'job', VSJobViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^analytics/', include(rrouter.urls)),
    url(r'^analytics/release/', ReleaseView.as_view()),
    url(r'^system/', include(arouter.urls)),
    url(r'^auth/', Auth.as_view()),
    url(r'^stats/', StatsView.as_view()),
    url(r'^analytics/predictevaluate', PredictionEvaluationView.as_view()),
    url(r'^analytics/predict', PredictionView.as_view()),
    url(r'^statshistory/', StatsHistoryView.as_view()),
    url(r'^docs/', include_docs_urls(title='visualSHARK ReST Documentation', public=False))
]
