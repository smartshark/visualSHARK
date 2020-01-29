#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
import logging
import sys
import os
import tarfile

from django.core.management.base import BaseCommand
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


    def handle(self, *args, **options):
        start = timeit.default_timer()

        for project in Project.objects.all():
            self.createCache(project)

        end = timeit.default_timer() - start
        self.stdout.write(self.style.SUCCESS('[OK]') + ' Finished in {:.3f}s '.format(end))

    def createCache(self, project):
        vcs_system = VCSSystem.objects(project_id=project.id).get()
        if(os.path.exists('repo_cache/' + project.name)):
            self.stdout.write(self.style.SUCCESS('[INFO]') + ' Project ' + project.name + ' will be ignored, since the data already exists')
            return
        content = vcs_system.repository_file.read()
        filename = 'repo_cache/' + project.name + ".tar.gz"
        with open(filename, "wb") as text_file:
            text_file.write(content)
            text_file.close()

        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall('repo_cache')
            tar.close()

        os.remove(filename)