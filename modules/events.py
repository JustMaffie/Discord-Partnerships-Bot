import discord
from partnersbot.module import Module

class Events(Module):
	def __init__(self, bot):
		super().__init__(bot)
		self.bot.owner = None

	async def on_ready(self):
		game = discord.Game(name=self._("PLAYING_STATUS_MESSAGE", "with partners"))
		await self.bot.change_presence(status=discord.Status.idle, game=game)
		info = [
			str(self.bot.user),
			self._("STARTUP_MESSAGE_DPY_VERSION", "Discord.py version: {}").format(discord.__version__),
			self._('STARTUP_MESSAGE_SHARD_AMOUNT', 'Shards: {}').format(self.bot.shard_count),
			self._('STARTUP_MESSAGE_GUILD_AMOUNT', 'Guilds: {}').format(len(self.bot.guilds)),
			self._('STARTUP_MESSAGE_USER_AMOUNT', 'Users: {}').format(len(set([m for m in self.bot.get_all_members()]))),
			self._('STARTUP_MESSAGE_COMMAND_MODULE_DATA', '{} modules with {} commands').format(len(self.bot.cogs), len(self.bot.commands))
		]
		self.logger.info("")
		for f in info:
			self.logger.info(f)
		self.bot.owner = await self.bot.application_info()
		for guild in self.bot.guilds:
            # Why not call the function instead of copy the code
			await self.on_guild_join(guild)

	async def on_guild_join(self, guild):
		if not guild.id in self.config.whitelist:
			await guild.leave()
			self.bot.logger.warn(self._("GUILD_NOT_WHITELISTED", "LEAVING GUILD {}, NOT WHITELISTED").format(guild.id))
            
def setup(bot):
	cog = Events(bot)
	bot.add_cog(cog)