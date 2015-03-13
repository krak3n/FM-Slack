"""
tests.test_slack
================

Tests for the Slack integration
"""

import mock
import unittest

from fmslack.cli import slack, query_api, slack_post


class BaseTestCase(unittest.TestCase):

    def setUp(self):

        # Requests patcher
        requests_patcher = mock.patch(
            'fmslack.cli.requests')
        self.requests = requests_patcher.start()
        self.addCleanup(requests_patcher.stop)

        # Logger patcher
        logger_patcher = mock.patch(
            'fmslack.cli.logger')
        self.logger = logger_patcher.start()
        self.addCleanup(logger_patcher.stop)


class TestQueryApi(BaseTestCase):

    def test_tracks_request(self):

        get = mock.MagicMock(status_code=200, data={'name':'some name'})
        self.requests.get.return_value = get
        response = query_api('http://api.thisissoon.fm', 'spotify_uri')

        self.requests.get.assert_called_once_with('http://api.thisissoon.fm/tracks/spotify_uri')

    def test_tracks_request_error(self):

        get = mock.MagicMock(status_code=404)
        self.requests.get.return_value = get
        response = query_api('http://api.thisissoon.fm', 'spotify_uri')

        self.logger.error.assert_called_once_with('API returned invalid status code 404')


class TestSlackPost(BaseTestCase):

    def test_slack_post(self):

        post = mock.MagicMock(status_code=200)
        self.requests.post.return_value = post
        track = {
            'name': 'track name',
            'artist': 'artist name',
            'album': 'album name',
            'image': 'http://albumimage.url'
        }

        response = slack_post('http://slack.com', track['name'], track['artist'], track['album'], track['image'])

        self.requests.post.assert_called_once()

    def test_slack_post_error(self):

        post = mock.MagicMock(status_code=401)
        self.requests.post.return_value = post
        track = {
            'name': 'track name',
            'artist': 'artist name',
            'album': 'album name',
            'image': 'http://albumimage.url'
        }

        response = slack_post('http://slack.com', track['name'], track['artist'], track['album'], track['image'])

        self.logger.error.assert_called_once()

