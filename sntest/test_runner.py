# -*- coding: utf-8 -*-

import mongoengine

from django.test.runner import DiscoverRunner


class MockDbTestRunner(DiscoverRunner):
    """This is currently used for MongoDb Mock runner."""

    def setup_databases(self, **kwargs):
        # this sets mongoengine to a mongomock connection
        mongoengine.connection.disconnect()
        mongoengine.connect('testdb', host='mongomock://localhost')

        # this keeps the testing setup normal for the mysql part (create test_default database)
        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        mongoengine.connection.disconnect()

        return super().teardown_databases(old_config, **kwargs)
