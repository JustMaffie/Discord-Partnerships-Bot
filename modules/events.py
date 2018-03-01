import discord

class Events:
	def __init__(self, bot):
		self.bot = bot
		self.bot.owner = None

	async def on_ready(self):
		bot = self.bot
		game = discord.Game(name=bot._("PLAYING_STATUS_MESSAGE", "with partners"))
		await bot.change_presence(status=discord.Status.idle, game=game)

	async def on_ready(self):
		info = ["\n", str(self.bot.user), "Discord.py version: {}".format(discord.__version__), 'Shards: {}'.format(self.bot.shard_count), 'Guilds: {}'.format(len(self.bot.guilds)),
			'Users: {}'.format(len(set([m for m in self.bot.get_all_members()]))), '{} modules with {} commands'.format(len(self.bot.cogs), len(self.bot.commands))]
		self.bot.logger.info("\n".join(info))
		self.bot.owner = await self.bot.application_info()

def setup(bot):
	cog = Events(bot)
	bot.add_cog(cog)