import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import traceback
import json
from partnersbot.module import Module

def get_applycmdname():
	with open("config.json") as f:
		ff = json.load(f)
		return ff.get("apply_command", {}).get("name", "apply")

def get_applycmd_cooldown():
	with open("config.json") as f:
		ff = json.load(f)
		return ff.get("apply_command", {}).get("cooldown", 300)

class Partnerships(Module):
	def __init__(self, bot):
		super().__init__(bot)
		self.f = [self._("PARTNERSHIPS_THANKS", "Thanks! "), self._("PARTNERSHIPS_ALRIGHT", "Alright! "), self._("PARTNERSHIPS_VERY_WELL", "Very well. ")]
		self.questions = self.config.questions
		self.timeout = self.config.apply_command.timeout
		self.db = None

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
		fields = []
		for question in questions:
			if first:
				await ctx.send(self.config.welcome_message+question['question'])
				try:
					msg = await self.bot.wait_for("message", check=check, timeout=self.timeout)
					fields.append({"embed_title": question['embed_title'], "answer": msg.content})
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
					fields.append({"embed_title": question['embed_title'], "answer": msg.content})
				except asyncio.TimeoutError:
					return await ctx.send(self._("PARTNERSHIPS_USER_INFO_CANCELLED", "Well, then not :wave:"))
				except:
					self.bot.logger.exception(traceback.format_exc())
					return await ctx.send(self._("PARTNERSHIPS_UNKNOWN_ERROR", "Something went wrong... Please try again later."))	
		await self.bot.manager.create_application(ctx.author.id, fields)
		await ctx.send(self._("PARTNERSHIPS_SUBMITTED", "Thanks for your application, it will be reviewed asap."))

def setup(bot):
	cog = Partnerships(bot)
	bot.add_cog(cog)
