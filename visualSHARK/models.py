#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import json
import uuid

from django.conf import settings
from django.db.models.signals import post_save
from django.db import models, transaction
from django.dispatch import receiver
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from mongoengine import connect
from pycoshark.mongomodels import Project, VCSSystem, Commit, Tag, File, CodeEntityState, FileAction, People, IssueSystem, Issue, Message, MailingList, Event, MynbouData, TravisBuild, Branch, Hunk

from visualSHARK.util.rmq import send_to_queue, send_to_user


# this is just because we do not have access to reindex the database and mongodb does not check for indexes but just creates them and if they are there does nothing
# nevertheless this requires the right to index stuff which we not have
def remove_index(cls):
    tmp = copy.deepcopy(cls._meta)
    if 'indexes' in tmp.keys():
        del tmp['indexes']
    del tmp['index_specs']
    tmp['index_specs'] = []
    return tmp

if not settings.TESTING:
    con = {'host': settings.DATABASES['mongodb']['HOST'],
           'port': settings.DATABASES['mongodb']['PORT'],
           'db': settings.DATABASES['mongodb']['NAME'],
           'username': settings.DATABASES['mongodb']['USER'],
           'password': settings.DATABASES['mongodb']['PASSWORD'],
           'authentication_source': settings.DATABASES['mongodb']['AUTHENTICATION_DB'],
           'connect': False}
    connect(**con)

    # these are the mongodb models which we directly use in the visualSHARK
    Project._meta = remove_index(Project)
    VCSSystem._meta = remove_index(VCSSystem)
    Commit._meta = remove_index(Commit)
    Tag._meta = remove_index(Tag)
    File._meta = remove_index(File)
    FileAction._meta = remove_index(FileAction)
    People._meta = remove_index(People)
    CodeEntityState._meta = remove_index(CodeEntityState)
    IssueSystem._meta = remove_index(IssueSystem)
    Issue._meta = remove_index(Issue)
    Message._meta = remove_index(Message)
    MailingList._meta = remove_index(MailingList)
    Event._meta = remove_index(Event)
    TravisBuild._meta = remove_index(TravisBuild)
    MynbouData._meta = remove_index(MynbouData)
    Branch._meta = remove_index(Branch)
    Hunk._meta = remove_index(Hunk)


if settings.TESTING:
    connect('test', host='mongomock://localhost')


class UserProfile(models.Model):
    """Fow now the userprofile only holds the channel.

    This can be extended to hold more information in the future, e.g.,
    customizable dashboards.
    """
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    channel = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username


# this is just for the token authentication for the rest-api
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        # create Token for the rest framework
        Token.objects.create(user=instance)
        # create user profile for channel
        UserProfile.objects.create(user=instance)


class ProjectStats(models.Model):
    """Contains project stats per day."""

    project_name = models.CharField(max_length=255)
    stats_date = models.DateField(auto_now=True)
    number_commits = models.IntegerField(default=0)
    number_issues = models.IntegerField(default=0)
    number_files = models.IntegerField(default=0)
    number_messages = models.IntegerField(default=0)
    number_people = models.IntegerField(default=0)

    def __str__(self):
        return self.project_name


class CommitGraph(models.Model):
    """Contains the raw data (pickle) and pre-computed graph nodes and their layout for the CommitGraph View."""

    vcs_system_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    directed_graph = models.FileField(blank=True, null=True, upload_to=settings.COMPUTED_FILES)
    directed_pickle = models.FileField(blank=True, null=True, upload_to=settings.COMPUTED_FILES)
    last_updated = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return self.title


class CommitLabelField(models.Model):
    """Contains currently available commit labels from labelSHARK.

    This needs to be synced with the fetch_commit_label_approaches command.
    """

    approach = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()

    @property
    def label(self):
        return '{}: {}'.format(self.approach, self.name)


# class VcsHistory(models.Model):
#     vcs_system_id = models.CharField(max_length=255)
#     date = models.DateField()
#     aggregate = models.FileField(blank=True, null=True, upload_to=settings.COMPUTED_FILES)
#     last_updated = models.DateTimeField(blank=True, null=True, auto_now=True)


class VSJobType(models.Model):
    """Possible types of jobs."""

    ident = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.ident


class VSJob(models.Model):
    """A Job with configuration and results."""

    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    executed_at = models.DateTimeField(blank=True, null=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_type = models.ForeignKey(VSJobType, on_delete=models.CASCADE)
    data = models.TextField()  # for now jsonized data (username, etc.)
    result = models.TextField(blank=True, null=True)
    error_count = models.IntegerField(default=0)  # number of tries for execution (error count)

    def __str__(self):
        return self.job_type.ident

    def requeue(self):
        send_to_queue(settings.QUEUE['job_queue'], {'job_type': self.job_type.ident, 'data': json.loads(self.data), 'job_id': self.pk})
        send_to_user(self.requested_by.profile.channel, {'msg': '{} job re-queued'.format(self.job_type.name), 'job_type': self.job_type.ident, 'created': True})

    @staticmethod
    @receiver(post_save, sender='visualSHARK.VSJob')
    def job_created(sender, instance, created, **kwargs):
        """Trigger the submission to the worker queue."""
        if created:
            # changes are saved but not committed to the database before the request finishes, so we hook on_commit with a callback
            def callme():
                send_to_queue(settings.QUEUE['job_queue'], {'job_type': instance.job_type.ident, 'data': json.loads(instance.data), 'job_id': instance.pk})
                send_to_user(instance.requested_by.profile.channel, {'msg': '{} job queued'.format(instance.job_type.name), 'job_type': instance.job_type.ident, 'created': True, 'job_id': instance.pk})
            transaction.on_commit(callme)

        # on save of the results we can also pass the result to the user
        if not created:
            send_to_user(instance.requested_by.profile.channel, {'msg': '{} job finished'.format(instance.job_type.name), 'job_type': instance.job_type.ident, 'created': False, 'success': instance.error_count == 0, 'job_id': instance.pk})
