import discord
import json
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_languages = {}  # Diccionario en memoria para idioma por usuario

def load_language(lang):
    with open(f'languages/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    channel = discord.utils.get(bot.get_all_channels(), name='general')
    if channel:
        msg = await channel.send(load_language('es')["welcome"])
        await msg.add_reaction('🇬🇧')
        await msg.add_reaction('🇨🇴')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    emoji = payload.emoji.name
    channel = bot.get_channel(payload.channel_id)

    # Solo permitimos uno a la vez
    if emoji == '🇬🇧':
        user_languages[payload.user_id] = 'en'
        await channel.send(f"{member.mention} has selected English.")
    elif emoji == '🇨🇴':
        user_languages[payload.user_id] = 'es'
        await channel.send(f"{member.mention} ha seleccionado Español.")

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return

    emoji = payload.emoji.name
    channel = bot.get_channel(payload.channel_id)

    # Si el emoji que quitó era de idioma, eliminamos el idioma registrado
    if emoji in ['🇬🇧', '🇨🇴']:
        if payload.user_id in user_languages:
            del user_languages[payload.user_id]
            user = await bot.fetch_user(payload.user_id)
            await channel.send(f"{user.mention} tu selección de idioma ha sido eliminada. Puedes elegir uno nuevo.")

@bot.command()
async def guide(ctx):
    lang = user_languages.get(ctx.author.id, 'en')
    data = load_language(lang)
    await ctx.send(data['how_to_use'])

@bot.command()
async def comandos(ctx):
    lang = user_languages.get(ctx.author.id, 'en')
    data = load_language(lang)
    await ctx.send(data['guia_comandos'])

@bot.command()
async def registrarse(ctx):
    lang = user_languages.get(ctx.author.id, 'en')
    data = load_language(lang)
    await ctx.send(data['registrarse'])

@bot.command()
async def canales(ctx):
    lang = user_languages.get(ctx.author.id, 'en')
    data = load_language(lang)
    await ctx.send(data['canales'])

bot.run(TOKEN)