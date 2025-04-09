from discord.ext import commands
from utils.language_handler import load_language, user_languages
import discord

def dm_only(ctx):
    return isinstance(ctx.channel, discord.DMChannel)

class GuideCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("GuideCommands cog loaded")

    @commands.command()
    async def guide(self, ctx):
        if not dm_only(ctx):
            try:
                await ctx.author.send("Please use commands in DM.")
            except discord.Forbidden:
                pass
            return
        lang = user_languages.get(ctx.author.id, 'en')
        data = load_language(lang)
        await ctx.send(data.get("how_to_use", "Guide information not available."))

    @commands.command()
    async def comandos(self, ctx):
        if not dm_only(ctx):
            try:
                await ctx.author.send("Please use commands in DM.")
            except discord.Forbidden:
                pass
            return
        lang = user_languages.get(ctx.author.id, 'en')
        data = load_language(lang)
        await ctx.send(data.get("guia_comandos", "Commands guide not available."))

    @commands.command()
    async def register(self, ctx):
        if not dm_only(ctx):
            try:
                await ctx.author.send("Please use commands in DM.")
            except discord.Forbidden:
                pass
            return
        lang = user_languages.get(ctx.author.id, 'en')
        data = load_language(lang)
        await ctx.send(data.get("registrarse", "Registration info not available."))

    @commands.command()
    async def channels(self, ctx):
        if not dm_only(ctx):
            try:
                await ctx.author.send("Please use commands in DM.")
            except discord.Forbidden:
                pass
            return
        lang = user_languages.get(ctx.author.id, 'en')
        data = load_language(lang)
        await ctx.send(data.get("canales", "Channels info not available."))

async def setup(bot):
    await bot.add_cog(GuideCommands(bot))