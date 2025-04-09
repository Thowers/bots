import discord
from discord.ext import commands
from utils.language_handler import load_language, user_languages
from services.spotify import get_playlist_by_genre, get_tracks_by_artist

def dm_only(ctx):
    return isinstance(ctx.channel, discord.DMChannel)

class RadioBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("🎵 RadioBot cargado.")

    @commands.command(name="playlist")
    async def playlist(self, ctx, *, genre_or_artist=None):
        if not dm_only(ctx):
            await ctx.author.send("Please use this command in DM.")
            return

        user_id = ctx.author.id
        lang = user_languages.get(user_id, "en")
        data = load_language(lang)

        if not genre_or_artist:
            msg = {
                "es": "Por favor escribe un género o artista después del comando.",
                "en": "Please type a genre or artist after the command."
            }.get(lang, "Please type a genre or artist.")
            await ctx.send(msg)
            return

        await ctx.send(data.get("buscando_spotify", "🔍 Searching Spotify..."))

        playlist_url = get_playlist_by_genre(genre_or_artist)
        if playlist_url:
            await ctx.send(data.get("playlist_encontrada", "🎧 Here's a playlist:") + f" {playlist_url}")
        else:
            tracks = get_tracks_by_artist(genre_or_artist)
            if tracks:
                await ctx.send(data.get("canciones_encontradas", "🎶 Top tracks:"))
                for track in tracks:
                    await ctx.send(track)
            else:
                await ctx.send(data.get("no_encontrado", "❌ Nothing found for that genre or artist."))

async def setup(bot):
    await bot.add_cog(RadioBot(bot))