"""
Read LICENSE file
"""
import logging
from discord.ext import commands
import discord
from .config import config_from_file
import os
import redis
from .i18n import I18N

class CustomContext(commands.Context):
	async def send_help(self):
		command = self.invoked_subcommand or self.command
		pages = await self.bot.formatter.format_help_for(self, command)
		ret = []
		for page in pages:
			ret.append(await self.send(page))
		return ret

# I'll just make it an auto sharded bot, in case someone is stupid enough to add this bot to 2500 servers
class Bot(commands.AutoShardedBot):
	def __init__(self, *args, **kwargs):
		self.config = config_from_file("config.json")
		self.logger = logging.getLogger("PartnersBot")
		super(Bot, self).__init__(command_prefix=self.config.command_prefix, *args, **kwargs)
		self.description = "An instance of JustMaffie's Partnerships Discord Bot"
		self._ = I18N(self)
		
		if self.config.redis.enabled:
			# Configure redis
			self.pool = redis.ConnectionPool(host=self.config.redis.host, port=self.config.redis.port, db=0)
			self.redis = redis.Redis(connection_pool=self.pool)

	async def get_context(self, message, *, cls=CustomContext):
		return await super().get_context(message, cls=cls)

	def load_extension(self, name):
		self.logger.info('LOADING EXTENSION {name}'.format(name=name))
		if not name.startswith("modules."):
			name = "modules.{}".format(name)
		return super().load_extension(name)

	def unload_extension(self, name):
		self.logger.info('UNLOADING EXTENSION {name}'.format(name=name))
		if not name.startswith("modules."):
			name = "modules.{}".format(name)
		return super().unload_extension(name)

	def load_all_extensions(self):
		_modules = [os.path.splitext(x)[0] for x in os.listdir("modules")]
		modules = []
		for module in _modules:
			if not module.startswith("_"):
				modules.append("modules.{}".format(module))

		for module in modules:
			self.load_extension(module)

	def run(self):
		super().run(self.config.token)

def make_bot(*args, **kwargs):
	bot = Bot(*args, **kwargs)
	bot.load_all_extensions()

	@bot.event
	async def on_command_error(ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send_help()
		elif isinstance(error, commands.BadArgument):
			await ctx.send_help()
		elif isinstance(error, commands.CommandInvokeError):
			message = "Error in command '{}'.\n{}".format(ctx.command.qualified_name, error)
			await ctx.send("```{message}```".format(message=message))
		elif isinstance(error, commands.CommandNotFound):
			pass
		elif isinstance(error, commands.CheckFailure):
			pass
		elif isinstance(error, commands.NoPrivateMessage):
			pass
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send("This command is on cooldown. "
						   "Try again in {:.2f}s".format(error.retry_after))
		else:
			bot.logger.exception(type(error).__name__, exc_info=error)

	return bot
