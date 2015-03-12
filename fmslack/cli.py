import click
import json
import requests
import urlparse

from redis import StrictRedis

@click.option('--redis-uri', '-r', required=True)
@click.option('--redis-channel', '-c', required=True)
@click.option('--slack-webhook-url', '-s')
@click.option('--api-url', '-a', required=True)
@click.command()
def slack(redis_uri, redis_channel, slack_webhook_url, api_url):

    uri = urlparse.urlparse(redis_uri)
    redis = StrictRedis(
        host=uri.hostname,
        port=int(uri.port),
        password=uri.password,
        db=0)

    pubsub = redis.pubsub()
    pubsub.subscribe(redis_channel)

    for item in pubsub.listen():
        if item.get('type') == 'message':
            data = json.loads(item.get('data'))
            if data['event'] == 'play':
                track = query_api(api_url, data['uri'])
                if track is not None:
                    print track
                    slack = slack_post(
                        slack_webhook_url,
                        track['name'],
                        track['album']['artists'][0]['name'],
                        track['album']['name'],
                        track['album']['images'][1]['url'])

                    if slack is None:
                        print 'slack error'

                else:
                    print 'failed'

def slack_post(slack_webhook_url, name, artist, album, image):
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
        return None

    return 'Success'

def query_api(api_url, uri):
    url = '{0}/tracks/{1}'.format(api_url, uri)
    r = requests.get(url)
    if not r.status_code == 200:
        return None

    try:
        return r.json()
    except ValueError:
        return None

def run():
    slack()
