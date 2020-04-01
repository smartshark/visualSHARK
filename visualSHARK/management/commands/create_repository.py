#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys
import os
import tarfile

from django.core.management.base import BaseCommand
from django.conf import settings

from visualSHARK.models import VCSSystem, Project

log = logging.getLogger()
log.setLevel(logging.DEBUG)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)


class Command(BaseCommand):

    help = 'Creates a repository cache for each project'

    def add_arguments(self, parser):
        parser.add_argument('project', help='which project')

    def handle(self, *args, **options):
        start = timeit.default_timer()

        if options['project'] == 'all':
            for project in Project.objects.all():
                self.create_repository(project)
        else:
            project = Project.objects.get(name__iexact=options['project'])
            self.create_repository(project)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))

    def create_repository(self, project):
        project_path = settings.LOCAL_REPOSITORY_PATH + project.name

        vcs_system = VCSSystem.objects(project_id=project.id).get()
        if(os.path.exists(project_path)):
            self.stdout.write(self.style.SUCCESS('[INFO]') + ' Project ' + project.name + ' will be ignored, since the data already exists')
            return

        content = vcs_system.repository_file.read()
        filename = settings.LOCAL_REPOSITORY_PATH + project.name + ".tar.gz"
        with open(filename, "wb") as arc:
            arc.write(content)
            arc.close()

        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall(settings.LOCAL_REPOSITORY_PATH)
            tar.close()

        os.remove(filename)