import partnersbot
import click

# We have to create the bot object to get access to redis
bot = partnersbot.make_bot(configLog=False)

@click.group()
def cli():
    pass

WHITELIST = "whitelist"

@cli.command()
@click.argument('guild')
def whitelist(guild):
    redis = bot.redis
    try:
        guild = int(guild)
    except:
        click.echo("The guild id must be an integer")
        return
    if redis.sismember(WHITELIST, guild):
        click.echo("This guild is already whitelisted!")
        return
    try:
        redis.sadd(WHITELIST, guild)
        click.echo("Guild added to the whitelist!")
    except:
        click.echo("An unknown error occurred!")

if __name__ == "__main__":
    cli()