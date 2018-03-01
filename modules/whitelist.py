import discord
from discord.ext import commands

WHITELIST_KEY = "whitelist"

class Whitelist:
    def __init__(self, bot):
        self.bot = bot
        if bot.config.redis.enabled:
            self.conn = bot.redis
        
    async def on_guild_join(self, guild):
        if not self.bot.config.redis.enabled:
            return
        if not self.conn.sismember(WHITELIST_KEY, guild.id) and not guild.id in self.bot.config.whitelist:
            # Guild not whitelisted, leave it now
            await guild.leave()
            self.bot.logger.warn(self.bot._("GUILD_NOT_WHITELISTED", "LEAVING GUILD {}, NOT WHITELISTED").format(guild.id))
            
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Why not call the function instead of copy the code
            await self.on_guild_join(guild)
            
    @commands.is_owner()
    @commands.group(aliases=['whitelist'])
    async def wh(self, ctx):
        if ctx.invoked_subcommand is None:
            if not self.bot.config.redis.enabled:
                return await ctx.send(self.bot._("WHITELIST_REDIS_UNAVAILABLE", "Redis is unavailable with the current config."))
            await ctx.send_help()
            
    @commands.is_owner()
    @wh.command()
    async def add(self, ctx, *, guild_id:int):
        if not self.bot.config.redis.enabled:
            return await ctx.send(self.bot._("WHITELIST_REDIS_UNAVAILABLE", "Redis is unavailable with the current config."))
        if self.conn.sismember(WHITELIST_KEY, guild_id):
            return await ctx.send(self.bot._("WHITELIST_GUILD_ALREADY_WHITELISTED", "This guild is already whitelisted!"))
        try:
            self.conn.sadd(WHITELIST_KEY, guild_id)
            return await ctx.send(self.bot._("WHITELIST_ADDED_GUILD_TO_WHITELIST", "Added this guild to the whitelist!"))
        except:
            return await ctx.send(self.bot._("WHITELIST_UNKNOWN_ERROR", "An unknown error occurred, is Redis still alive?"))
            
    @commands.is_owner()
    @wh.command()
    async def get(self, ctx):
        if not self.bot.config.redis.enabled:
            return await ctx.send(self.bot._("WHITELIST_REDIS_UNAVAILABLE", "Redis is unavailable with the current config."))
        _guilds = self.conn.smembers(WHITELIST_KEY)
        guilds = []
        for guild in _guilds:
            guilds.append(guild.decode())
        await ctx.send("```\n{}\n```".format("\n".join(guilds)))
            
    @commands.is_owner()
    @wh.command()
    async def remove(self, ctx, *, guild_id:int):
        if not self.bot.config.redis.enabled:
            return await ctx.send(self.bot._("WHITELIST_REDIS_UNAVAILABLE", "Redis is unavailable with the current config."))
        if not self.conn.sismember(WHITELIST_KEY, guild_id):
            return await ctx.send(self.bot._("WHITELIST_GUILD_NOT_WHITELISTED", "This guild is not whitelisted!"))
        try:
            self.conn.srem(WHITELIST_KEY, guild_id)
            return await ctx.send(self.bot._("WHITELIST_GUILD_REMOVED_FROM_WHITELIST", "Removed this guild from the whitelist!"))
        except:
            return await ctx.send(self.bot._("WHITELIST_UNKNOWN_ERROR", "An unknown error occurred, is Redis still alive?"))

def setup(bot):
    cog = Whitelist(bot)
    bot.add_cog(cog)
