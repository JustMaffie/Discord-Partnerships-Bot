import discord
from discord.ext import commands

WHITELIST_KEY = "whitelist"

class Whitelist:
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.redis
        
    async def on_guild_join(self, guild):
        if not self.conn.sismember(WHITELIST_KEY, guild.id):
            # Guild not whitelisted, leave it now
            await guild.leave()
            
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Why not call the function instead of copy the code
            await self.on_guild_join(guild)
            
    @commands.is_owner()
    @commands.group(aliases=['whitelist'])
    async def wh(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            
    @commands.is_owner()
    @wh.command()
    async def add(self, ctx, *, guild_id:int):
        if self.conn.sismember(WHITELIST_KEY, guild_id):
            return await ctx.send("This guild is already whitelisted!")
        try:
            self.conn.sadd(WHITELIST_KEY, guild_id)
            return await ctx.send("Added this guild to the whitelist!")
        except:
            return await ctx.send("An unknown error occurred, is Redis still alive?")
            
    @commands.is_owner()
    @wh.command()
    async def get(self, ctx):
        _guilds = self.conn.smembers(WHITELIST_KEY)
        guilds = []
        for guild in _guilds:
            guilds.append(guild.decode())
        await ctx.send("```\n{}\n```".format("\n".join(guilds)))
            
    @commands.is_owner()
    @wh.command()
    async def remove(self, ctx, *, guild_id:int):
        if not self.conn.sismember(WHITELIST_KEY, guild_id):
            return await ctx.send("This guild is not whitelisted!")
        try:
            self.conn.srem(WHITELIST_KEY, guild_id)
            return await ctx.send("Removed this guild from the whitelist!")
        except:
            return await ctx.send("An unknown error occurred, is Redis still alive?")

def setup(bot):
    cog = Whitelist(bot)
    bot.add_cog(cog)