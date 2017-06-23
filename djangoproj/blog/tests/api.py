import json
import unittest
from unittest.mock import patch

import fakeredis
from rest_framework.test import APISimpleTestCase


TOP_10_SAMPLE = {
    'data': 100, 'one': 73, 'new': 68,
    'project': 65, 'time': 62, 'use': 61,
    'work': 61, 'us': 58, 'software': 58, 'user': 58
}

TOP_10_PERCENTAGE_SAMPLE = {
    'data': 0.84, 'one': 0.61, 'new': 0.57, 'project': 0.55,
    'time': 0.52, 'use': 0.51, 'work': 0.51, 'us': 0.49,
    'software': 0.49, 'user': 0.49
}


@patch('blog.views.connection', fakeredis.FakeRedis())
class ApiTestCase(APISimpleTestCase):
    """
    We put stuff to redis, call api, compare data from redis and api.
    """

    def setUp(self):
        # Setup fake redis for testing.
        self.r = fakeredis.FakeRedis()
        self.r.set('top_10', json.dumps(TOP_10_SAMPLE))
        self.r.set('top_10_percentage', json.dumps(TOP_10_PERCENTAGE_SAMPLE))
        self.r.set(
            'top_10_per_author_percentage',
            json.dumps({'somename': TOP_10_PERCENTAGE_SAMPLE})
        )
        self.r.set(
            'top_10_per_author',
            json.dumps({'somename': TOP_10_SAMPLE})
        )

    def tearDown(self):
        # Clear data in fakeredis.
        self.r.flushall()

    def test_count(self):
        # I don't use reverse here, as `stats` is a part of specification.
        data = self.client.get('/stats/').json()
        self.assertEqual(data, TOP_10_SAMPLE)

    def test_freqs(self):
        data = self.client.get('/stats/?percent').json()
        self.assertEqual(data, TOP_10_PERCENTAGE_SAMPLE)

    def test_count_per_author(self):
        data = self.client.get('/stats/somename/').json()
        self.assertEqual(data, TOP_10_SAMPLE)

    def test_freqs_per_author(self):
        data = self.client.get('/stats/somename/?percent').json()
        self.assertEqual(data, TOP_10_PERCENTAGE_SAMPLE)

    @unittest.skip
    def test_similarities(self):
        raise NotImplementedError
