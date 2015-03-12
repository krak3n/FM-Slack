import click

def run():
    slack(auto_envar_prefix='FM_SLACK')

@click.option('--redis-uri', '-r', required=True)
@click.option('--redis-channel', '-c', required=True)
@click.option('--slack-webhook-url', '-s', required=True)
@click.command()
def slack(redis_uri, redis_channel, slack_webhook_url):
    print redis_uri
