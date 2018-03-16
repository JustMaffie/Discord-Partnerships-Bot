import discord

class Events:
	def __init__(self, bot):
		self.bot = bot
		self.bot.owner = None

	async def on_ready(self):
		bot = self.bot
		game = discord.Game(name=bot._("PLAYING_STATUS_MESSAGE", "with partners"))
		await bot.change_presence(status=discord.Status.idle, game=game)
		info = [
			str(self.bot.user),
			self.bot._("STARTUP_MESSAGE_DPY_VERSION", "Discord.py version: {}").format(discord.__version__),
			self.bot._('STARTUP_MESSAGE_SHARD_AMOUNT', 'Shards: {}').format(self.bot.shard_count),
			self.bot._('STARTUP_MESSAGE_GUILD_AMOUNT', 'Guilds: {}').format(len(self.bot.guilds)),
			self.bot._('STARTUP_MESSAGE_USER_AMOUNT', 'Users: {}').format(len(set([m for m in self.bot.get_all_members()]))),
			self.bot._('STARTUP_MESSAGE_COMMAND_MODULE_DATA', '{} modules with {} commands').format(len(self.bot.cogs), len(self.bot.commands))
		]
		self.bot.logger.info("")
		for f in info:
			self.bot.logger.info(f)
		self.bot.owner = await self.bot.application_info()

def setup(bot):
	cog = Events(bot)
	bot.add_cog(cog)