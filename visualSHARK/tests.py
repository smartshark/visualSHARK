"""Some assortet tests of functionality."""

import json
import importlib

from django.test import TestCase

from visualSHARK.util.helper import Label
from visualSHARK.models import Project, VCSSystem, Commit


class ExporterTests(TestCase):
    """Test the export for the technology labeling."""

    def _load_fixture(self):
        pass

    def test_export(self):
        pass


class HelperTests(TestCase):
    """This tests the helpers."""

    def _load_fixture(self, fixture_name):

        # this would be nice but it does not work
        # db = _get_db()
        # db.connection.drop_database('testdb')

        self._ids = {}

        # we really have to iterate over collections
        for col in ['Project', 'VCSSystem', 'File', 'Commit', 'FileAction', 'CodeEntityState', 'Hunk']:
            module = importlib.import_module('visualSHARK.models')
            obj = getattr(module, col)
            obj.drop_collection()

        fixture = json.load(open('visualSHARK/fixtures/{}.json'.format(fixture_name), 'r'))
        for col in fixture['collections']:

            module = importlib.import_module('visualSHARK.models')
            obj = getattr(module, col['model'])

            for document in col['documents']:
                tosave = document.copy()
                had_id_mapping = False

                for k, v in document.items():
                    if k == 'id':
                        self._ids[document['id']] = None
                        del tosave['id']
                        had_id_mapping = True
                    if type(v) not in [int] and v.startswith('{') and v.endswith('}'):
                        tosave[k] = self._ids[v.replace('{', '').replace('}', '')]

                r = obj(**tosave)
                r.save()
                if had_id_mapping:
                    self._ids[document['id']] = r.id

    # def test_fixtures(self):
    #     self.assertEqual(len(Project.objects.all()), 0)
    #     self.assertEqual(len(VCSSystem.objects.all()), 0)

    #     self._load_fixture('entity_matching')
    #     projects = Project.objects.all()
    #     self.assertEqual(len(projects), 1)

    #     vcs = VCSSystem.objects.all()
    #     self.assertEqual(len(vcs), 1)
    #     self.assertEqual(vcs[0].project_id, projects[0].id)

    def test_entity_matching(self):

        # this removes method a, it should return no affected entities
        self._load_fixture('entity_matching')

        l = Label()
        entities = l.generate_affected_entities(Commit.objects.get(id=self._ids['commit2']), self._ids['fileaction2'])
        self.assertEqual(len(entities), 0)
