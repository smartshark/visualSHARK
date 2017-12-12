from datetime import datetime

from django.test import TestCase
from pymongo import MongoClient

from visualSHARK.models import Project


class GraphTests(TestCase):
    # fixtures = ['base']

    def setUp(self):
        c = MongoClient(host='mongomock://localhost')
        self._db = c.test

        t1 = self._db.Project.insert_one({"name": 'Testproject'})
        t2 = self._db.VCSSystem.insert_one({"url": 'http://localhost/testproject.git', "project_id": t1.inserted_id, 'repository_type': 'git', 'last_updated': datetime.now()})

        p1 = self._db.People.insert_one({'email': 'testuser@test.local', 'name': 'Test User', 'username': 'testuser'})
        c = self._db.Commit.insert_one({'vcs_system_id': t2.inserted_id, 'revision_hash': 'abc', 'author_id': p1.inserted_id, 'author_date': datetime.now(), 'committer_id': p1.inserted_id, 'committer_date': datetime.now(), 'message': 'initial commit'})

    def test_projects(self):
        np = len(Project.objects.all())
        self.assertEqual(np, 1)
