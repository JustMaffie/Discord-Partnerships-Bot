import discord
from discord.ext import commands

WHITELIST_KEY = "whitelist"

class Whitelist:
    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild):
        if not guild.id in self.bot.config.whitelist:
            await guild.leave()
            self.bot.logger.warn(self.bot._("GUILD_NOT_WHITELISTED", "LEAVING GUILD {}, NOT WHITELISTED").format(guild.id))
            
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Why not call the function instead of copy the code
            await self.on_guild_join(guild)
            
def setup(bot):
    cog = Whitelist(bot)
    bot.add_cog(cog)
