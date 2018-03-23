import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import traceback
import json
import datetime
from partnersbot.module import Module

def get_applycmdname():
	with open("config.json") as f:
		ff = json.load(f)
		return ff.get("apply_command_name", "apply")

def get_applycmd_cooldown():
	with open("config.json") as f:
		ff = json.load(f)
		return ff.get("apply_command_cooldown", 300)

class Partnerships(Module):
	def __init__(self, bot):
		super().__init__(bot)
		self.f = [self._("PARTNERSHIPS_THANKS", "Thanks! "), self._("PARTNERSHIPS_ALRIGHT", "Alright! "), self._("PARTNERSHIPS_VERY_WELL", "Very well. ")]
		self.questions = self.config.questions
		self.output = self.getOutput(self.config.output)
		self.timeout = 60
		self.db = None

	async def on_ready(self):
		self.output = self.getOutput(self.config.output)

	def getOutput(self, id):
		output = self.bot.get_channel(id=id)
		return output

	@commands.command(name=get_applycmdname())
	@commands.cooldown(1, get_applycmd_cooldown(), type=BucketType.user)
	async def apply(self, ctx):
		"""Start the interactive partner application prompt."""
		if self.config.dm_only:
			if not isinstance(ctx.message.channel, discord.DMChannel):
				return
		questions = self.questions
		first = True
		def check(m):
			return m.author.id == ctx.message.author.id and m.channel.id == ctx.message.channel.id
		embed = discord.Embed(timestamp=datetime.datetime.utcnow())
		embed.colour = discord.Color.blue()
		embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
		embed.set_footer(text="User ID: {}".format(ctx.author.id))
		embed.set_thumbnail(url=ctx.message.author.avatar_url)
		for question in questions:
			if first:
				await ctx.send(self.config.welcome_message+question['question'])
				try:
					msg = await self.bot.wait_for("message", check=check, timeout=self.timeout)
					embed.add_field(name=question['embed_title'], value=msg.content)
				except asyncio.TimeoutError:
					return await ctx.send(self._("PARTNERSHIPS_USER_INFO_CANCELLED", "Well, then not :wave:"))
				except:
					self.bot.logger.exception(traceback.format_exc())
					return await ctx.send(self._("PARTNERSHIPS_UNKNOWN_ERROR", "Something went wrong... Please try again later."))
				first = False
			else:
				await ctx.send(random.choice(self.f) + question['question'])
				try:
					msg = await self.bot.wait_for("message", check=check, timeout=self.timeout)
					embed.add_field(name=question['embed_title'], value=msg.content)
				except asyncio.TimeoutError:
					return await ctx.send(self._("PARTNERSHIPS_USER_INFO_CANCELLED", "Well, then not :wave:"))
				except:
					self.bot.logger.exception(traceback.format_exc())
					return await ctx.send(self._("PARTNERSHIPS_UNKNOWN_ERROR", "Something went wrong... Please try again later."))	
		await self.output.send(embed=embed)
		await ctx.send(self._("PARTNERSHIPS_SUBMITTED", "Thanks for your application, it will be reviewed asap."))

def setup(bot):
	cog = Partnerships(bot)
	bot.add_cog(cog)
