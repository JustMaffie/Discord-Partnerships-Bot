"""
Read LICENSE file
"""

import discord
from discord.ext import commands
import datetime
from collections import Counter
import io
import textwrap
import traceback
from contextlib import redirect_stdout

def is_owner():
    def check(ctx):
        owners = ctx.bot.config.owners
        return ctx.author.id in owners
    return commands.check(check)
commands.is_owner = is_owner
class Owner:

	def __init__(self, bot):
		self.bot = bot

	def cleanup_code(self, content):
		if content.startswith('```') and content.endswith('```'):
			return '\n'.join(content.split('\n')[1:-1])
		return content.strip('` \n')

	def get_syntax_error(self, e):
		if e.text is None:
			return '```py\n{e.__class__.__name__}: {e}\n```'.format(e=e)
		return '```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'.format(e=e)

	@commands.is_owner()
	@commands.command()
	async def reload(self, ctx, module):
		try:
			self.bot.unload_extension(module)
			self.bot.load_extension(module)
		except Exception as e:
			await ctx.send("An error occurred while reloading {module}\n``{e}``".format(module=module,e=e))
			self.bot.logger.exception(traceback.format_exc)
		else:
			await ctx.send("Module {module} reloaded successfully".format(module=module))

	@commands.is_owner()
	@commands.command()
	async def load(self, ctx, module):
		try:
			self.bot.load_extension(module)
		except Exception as e:
			self.bot.logger.exception(traceback.format_exc)
			return await ctx.send("An error occurred while loading {module}\n{e}".format(module=module,e=e))
		return await ctx.send("Module {module} loaded successfully".format(module=module))

	@commands.is_owner()
	@commands.command()
	async def unload(self, ctx, module):
		try:
			self.bot.unload_extension(module)
		except Exception as e:
			self.bot.logger.exception(traceback.format_exc)
			return await ctx.send("An error occurred while loading {module}\n{e}".format(module=module,e=e))
		return await ctx.send("Module {module} loaded successfully".format(module=module))

	@commands.is_owner()
	@commands.command()
	async def about(self, ctx):
		embed = discord.Embed()
		embed.color = discord.Colour.blue()
		embed.add_field(name=self.bot._("ABOUT_DPY_VERSION", "Discord.py version"), value=discord.__version__)
		embed.add_field(name=self.bot._("ABOUT_AUTHOR", "Author"), value="[JustMaffie](https://github.com/JustMaffie)")
		embed.add_field(name=self.bot._("ABOUT_BOT_LINK", "Bot Link"), value="[github.com/JustMaffie/Discord-Partnerships-Bot](https://github.com/JustMaffie/Discord-Partnerships-Bot)")
		if self.bot.owner:
			owner = self.bot.owner.owner
			embed.add_field(name=self.bot._("ABOUT_INSTANCE_OWNED_BY", "Instance Owned By"), value="{}#{}".format(owner.name, owner.discriminator))
		embed.add_field(name=self.bot._("ABOUT_BOT_TITLE", "About this bot"), value=self.bot._("ABOUT_BOT_VALUE", "This bot is an instance of JustMaffie's Partnerships Bot, an open source discord bot to take some load off your shoulders."))
		return await ctx.send(embed=embed)

	# Thanks danny
	@commands.command(name='eval')
	@commands.is_owner()
	async def _eval(self, ctx, *, body: str):
		env = {
			'bot': self.bot,
			'ctx': ctx,
			'channel': ctx.channel,
			'author': ctx.author,
			'guild': ctx.guild,
			'message': ctx.message,
		}

		env.update(globals())

		body = self.cleanup_code(body)
		stdout = io.StringIO()

		to_compile = 'async def func():\n{}'.format(textwrap.indent(body, "  "))

		try:
			exec(to_compile, env)
		except Exception as e:
			return await ctx.send('```py\n{e.__class__.__name__}: {e}\n```').format(e=e)

		func = env['func']
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception as e:
			value = stdout.getvalue()
			await ctx.send('```py\n{}{}\n```').format(value, traceback.format_exc())
		else:
			value = stdout.getvalue()
			try:
				await ctx.message.add_reaction('\u2705')
			except:
				pass

			if ret is None:
				if value:
					await ctx.send('```py\n{}\n```'.format(value))
			else:
				self._last_result = ret
				await ctx.send('```py\n{}{}\n```'.format(value,ret))


def setup(bot):
	cog = Owner(bot)
	bot.add_cog(cog)