"""
tests.test_slack
================

Tests for the Slack integration
"""

import mock
import unittest
import requests

from fmslack.cli import slack, query_api, slack_post


# Example response from FM API
TRACK_DATA = {
    'album': {
        'artists': [{
            'name': 'artist name',
        }],
        'name': 'album name'
    },
    'name': 'track name',
    'image': 'http://albumimage.url'
}


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

        self.requests.get.assert_called_once_with(
            'http://api.thisissoon.fm/tracks/spotify_uri')

    def test_tracks_status_error(self):

        get = mock.MagicMock(status_code=404)
        self.requests.get.return_value = get
        response = query_api('http://api.thisissoon.fm', 'spotify_uri')

        self.logger.error.assert_called_once_with(
            'API returned invalid status code 404')

    def test_tracks_request_error(self):

        self.requests.get.side_effect = requests.exceptions.RequestException()
        self.assertRaises(
            requests.exceptions.RequestException,
            query_api,
            'http://api.thisissoon.fm',
            'spotify_uri')


class TestSlackPost(BaseTestCase):

    def test_slack_post(self):

        post = mock.MagicMock(status_code=200)
        self.requests.post.return_value = post

        response = slack_post(
            'http://slack.com',
            TRACK_DATA['name'],
            TRACK_DATA['album']['artists'][0]['name'],
            TRACK_DATA['album']['name'],
            TRACK_DATA['image'])

        assert self.requests.post.call_count == 1

    def test_slack_post_status_error(self):

        post = mock.MagicMock(status_code=401)
        self.requests.post.return_value = post

        response = slack_post(
            'http://slack.com',
            TRACK_DATA['name'],
            TRACK_DATA['album']['artists'][0]['name'],
            TRACK_DATA['album']['name'],
            TRACK_DATA['image'])

        self.logger.error.assert_called_once_with('Slack returned invalid status code 401')

    def test_slack_post_request_error(self):

        self.requests.post.side_effect = requests.exceptions.RequestException()
        self.assertRaises(
            requests.exceptions.RequestException,
            slack_post,
            'http://slack.com',
            TRACK_DATA['name'],
            TRACK_DATA['album']['artists'][0]['name'],
            TRACK_DATA['album']['name'],
            TRACK_DATA['image'])
