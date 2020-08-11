#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from visualSHARK.models import Project
from visualSHARK.models import ProjectAttributes


class Command(BaseCommand):
    help = 'Create Project Attributes'

    def handle(self, *args, **options):

        for pro in Project.objects.all():

            ps, created = ProjectAttributes.objects.get_or_create(project_name=pro.name)

            if created:
                self.stdout.write(self.style.SUCCESS('[OK]') + ' Creating Attribute for Project {}'.format(pro.name))

            ps.save()
