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
@click.option('--redis-uri', '-r', required=True)
@click.option('--redis-channel', '-c', required=True)
@click.option('--slack-webhook-url', '-s')
@click.option('--api-url', '-a', required=True)
@click.command()
def slack(redis_uri, redis_channel, slack_webhook_url, api_url, log_level):

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
                    logger.debug('API returned track data for {0}'.format(track['spotify_uri']))
                    slack = slack_post(
                        slack_webhook_url,
                        track['name'],
                        track['album']['artists'][0]['name'],
                        track['album']['name'],
                        track['album']['images'][2]['url'])

def slack_post(slack_webhook_url, name, artist, album, image):
    logger.debug('Posting to Slack webhook {0}'.format(slack_webhook_url))
    payload = {
        'attachments': [
            {
                'fallback': 'Playing ' + name,
                'text': 'Playing ' + name,
                'fields': [
                    {
                        'title': 'Artist',
                        'value': artist,
                        'short': 'true'
                    },{
                        'title': 'Album',
                        'value': album,
                        'short': 'true'
                    }
                ],
                'image_url': image,
            }
        ]
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(slack_webhook_url, data=json.dumps(payload), headers=headers)
    if not r.status_code == 200:
        logger.error('Slack returned invalid status code {0}'.format(r.status_code))

def query_api(api_url, uri):
    url = '{0}/tracks/{1}'.format(api_url, uri)
    r = requests.get(url)
    if not r.status_code == 200:
        logger.error('API returned invalid status code {0}'.format(r.status_code))
        return None

    try:
        return r.json()
    except ValueError:
        return None

def run():
    slack()
