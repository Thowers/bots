import discord
from discord.ext import commands
from utils.language_handler import load_language, user_languages
from utils.spotify import get_tracks_by_artist
import asyncio
from discord.ui import Button, View

class RadioBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("RadioBot cargado.")

    @commands.command(name="playlist")
    async def playlist(self, ctx, *, genre_or_artist=None):
        user_id = ctx.author.id
        lang = user_languages.get(user_id, "en")
        data = load_language(lang)

        if not genre_or_artist:
            msg = {
                "es": "Por favor escribe un género o artista después del comando.",
                "en": "Please type a genre or artist after the command."
            }.get(lang, "Please type a genre or artist.")
            await ctx.send(msg, ephemeral=True)
            return

        await ctx.send(data.get("buscando_spotify", "🔍 Searching Spotify..."), ephemeral=True)

        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            await ctx.send({
                "es": "❌ No estás conectado a un canal de voz.",
                "en": "❌ You are not connected to a voice channel."
            }.get(lang, "❌ You are not connected to a voice channel."), ephemeral=True)
            return

        voice_channel = voice_state.channel
        await ctx.send(data.get("canciones_encontradas", "🎶 Top tracks:") + f"\n➡️ Canal detectado: {voice_channel.name}", ephemeral=True)

        tracks = get_tracks_by_artist(genre_or_artist)
        if tracks:
            for track in tracks:
                song_info = f"{track['name']} - {track['artist']}"
                button = Button(label="Agregar a Muzox", style=discord.ButtonStyle.primary)

                async def button_callback(interaction, info=song_info):
                    await interaction.response.send_message(f"{info}", ephemeral=True)
                    await interaction.message.delete()

                button.callback = button_callback

                view = View()
                view.add_item(button)

                await ctx.send(f"{song_info}", view=view, ephemeral=True)
                await asyncio.sleep(2)
        else:
            await ctx.send(data.get("no_encontrado", "❌ Nothing found for that genre or artist."), ephemeral=True)

async def setup(bot):
    await bot.add_cog(RadioBot(bot))