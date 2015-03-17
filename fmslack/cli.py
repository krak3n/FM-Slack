#!/usr/bin/env python
# encoding: utf-8

"""
fmslack.cli
===========

CLI interface for FM Slack.
"""

import click
import json
import logging
import requests
import urlparse

from redis import StrictRedis


LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"

logger = logging.getLogger('fmslack')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)


@click.option(
    '--log-level',
    '-l',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    default='ERROR')
@click.option(
    '--redis-uri',
    '-r',
    help='e.g: redis://localhost:6379/',
    default='redis://localhost:6379/')
@click.option(
    '--redis-channel',
    '-c',
    help='Channel to listen on for events',
    required=True)
@click.option('--slack-webhook-url', '-s', help='Webhook URL of slack integration')
@click.option('--api-url', '-a', help='URL of FM API server', required=True)
@click.command()
def slack(redis_uri, redis_channel, slack_webhook_url, api_url, log_level):
    """Listens for play event on redis channel. On play event, retrieves
    track data from FM API and triggers post to Slack.

    Arguments
    ---------
    redis_uri : str
        URI of redis server
    redis_channel : str
        Channel to listen on for events
    slack_webhook_url : str
        Webhook URL of slack integration
    api_url : str
        URL of FM API server
    log_level : str
        Logging level
    """

    logger.setLevel(logging.getLevelName(log_level))
    logger.info('Starting..')

    uri = urlparse.urlparse(redis_uri)
    redis = StrictRedis(
        host=uri.hostname,
        port=int(uri.port),
        password=uri.password,
        db=0)

    logger.debug('Connecting to redis at: {0}'.format(redis_uri))

    pubsub = redis.pubsub()
    pubsub.subscribe(redis_channel)

    logger.debug('Subscribed to redis channel: {0}'.format(redis_channel))

    for item in pubsub.listen():
        if item.get('type') == 'message':
            data = json.loads(item.get('data'))
            if data['event'] == 'play':
                logger.info('Event: PLAY')
                track = query_api(api_url, data['uri'])
                if track is not None:
                    logger.debug('API returned track data for {0}'.format(
                        track['spotify_uri']))
                    slack_post(
                        slack_webhook_url,
                        track['name'],
                        track['album']['artists'][0]['name'],
                        track['album']['name'],
                        track['album']['images'][2]['url'])


def slack_post(slack_webhook_url, name, artist, album, image):
    """ Post to slack incoming webhook.

    Arguments
    ---------
    slack_webhook_url : str
        Webhook URL of slack integration
    name : str
        Track name to post
    artist : str
        Artist name to post
    album : str
        Album name to post
    image : str
        Album image to post
    """

    logger.debug('Posting to Slack webhook {0}'.format(slack_webhook_url))

    payload = {
        "text": "Now playing: *{artist} - {album}: {name}*".format(
            artist=artist,
            album=album,
            name=name),
        "channel": "#general",
        "username": "thisissoon.fm",
        "icon_url": image
    }

    try:
        response = requests.post(
            slack_webhook_url,
            data=json.dumps(payload),
            headers={
                'content-type': 'application/json'
            })
    except requests.exceptions.RequestException as error:
        logger.error(error)

    if not response.status_code == 200:
        logger.error('Slack returned invalid status code {0}'.format(response.status_code))


def query_api(api_url, uri):
    """ Get track data from FM API.

    Arguments
    ---------
    api_url : str
        URL of FM API server
    uri : str
        spotify uri of track to request

    Returns
    -------
    dict
        response from API with track data
    """

    url = '{0}/tracks/{1}'.format(api_url, uri)

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as error:
        logger.error(error)
        return None

    if not response.status_code == 200:
        logger.error('API returned invalid status code {0}'.format(response.status_code))
        return None

    try:
        return response.json()
    except ValueError:
        return None


def run():
    """ Main run command used for the entry point.
    """

    slack(auto_envvar_prefix='FM_SLACK')
