"""
Read LICENSE file
"""
import logging
from discord.ext import commands
import discord
from .config import config_from_file
import os
from .i18n import I18N
from .applications import ApplicationManager

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
	def __init__(self, logger, *args, **kwargs):
		self.config = config_from_file("config.json")
		self._ = I18N(self)
		self.logger = logger
		self.mongo = None
		self.db = None
		super(Bot, self).__init__(command_prefix=self.config.command_prefix, *args, **kwargs)
		if self.config.database.enabled:
			import motor.motor_asyncio
			self.mongo = motor.motor_asyncio.AsyncIOMotorClient(host=self.config.database.host, port=self.config.database.port, io_loop=self.loop)
			self.db = self.mongo[self.config.database.database]
		self.description = self._("BOT_DESCRIPTION", "An instance of JustMaffie's Partnerships Discord Bot")

	def reload_config(self):
		self.config = config_from_file("config.json")

	async def get_context(self, message, *, cls=CustomContext):
		return await super().get_context(message, cls=cls)

	def load_extension(self, name):
		self.logger.info(self._("LOADING_EXTENSION", 'LOADING EXTENSION {name}').format(name=name))
		if not name.startswith("modules."):
			name = "modules.{}".format(name)
		return super().load_extension(name)

	def unload_extension(self, name):
		self.logger.info(self._("UNLOADING_EXTENSION", 'UNLOADING EXTENSION {name}').format(name=name))
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

def make_bot(logger, *args, **kwargs):
	bot = Bot(logger, *args, **kwargs)
	bot.load_all_extensions()

	@bot.event
	async def on_ready():
		if bot.db:
			if bot.config.database.auth.enabled:
				await bot.db.authenticate(bot.config.database.auth.username, bot.config.database.auth.password)
			bot.manager = ApplicationManager(bot)

	@bot.event
	async def on_command_error(ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send_help()
		elif isinstance(error, commands.BadArgument):
			await ctx.send_help()
		elif isinstance(error, commands.CommandInvokeError):
			message = bot._("ERROR_IN_COMMAND", "Error in command '{}'.\n{}").format(ctx.command.qualified_name, error)
			await ctx.send("```{message}```".format(message=message))
		elif isinstance(error, commands.CommandNotFound):
			pass
		elif isinstance(error, commands.CheckFailure):
			pass
		elif isinstance(error, commands.NoPrivateMessage):
			pass
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send(bot._("COMMAND_IN_COOLDOWN", "This command is on cooldown. "
						   "Try again in {:.2f}s").format(error.retry_after))
		else:
			bot.logger.exception(type(error).__name__, exc_info=error)

	return bot
