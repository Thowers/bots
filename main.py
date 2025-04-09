import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.language_handler import load_language, user_languages
from modules import guide_bot, agend_bot, radio_bot
import asyncio
import nest_asyncio
nest_asyncio.apply()


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    for guild in bot.guilds:
        general_channel = discord.utils.get(guild.text_channels, name='general')
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    async for msg in general_channel.history(limit=None):
                        await msg.delete()
                    msg = await channel.send(load_language('es')["welcome"])
                    await msg.add_reaction('🇬🇧')
                    await msg.add_reaction('🇨🇴')
                    break
                except Exception as e:
                    print(f"Error al enviar mensaje en {channel.name}: {e}")
        break

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    emoji = payload.emoji.name
    user = await bot.fetch_user(payload.user_id)

    if emoji == '🇬🇧':
        user_languages[payload.user_id] = 'en'
        try:
            await user.send("You've selected English! Use commands like `!comandos`, or `!register`,  here in DM.")
        except discord.Forbidden:
            print(f"Cannot DM user {user.name} (permissions issue).")
    elif emoji == '🇨🇴':
        user_languages[payload.user_id] = 'es'
        try:
            await user.send("Has seleccionado Español. Usa comandos como `!comandos`, o `!register` aquí por DM.")
        except discord.Forbidden:
            print(f"Cannot DM user {user.name} (permissions issue).")

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return

    emoji = payload.emoji.name
    if emoji in ['🇬🇧', '🇨🇴']:
        if payload.user_id in user_languages:
            del user_languages[payload.user_id]
            user = await bot.fetch_user(payload.user_id)
            try:
                await user.send("Your language selection has been removed. Please react again to choose a language.")
            except discord.Forbidden:
                print(f"Cannot DM user {user.name}.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        print(f"[DM] {message.author}: {message.content}")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("No entendí ese comando. Intenta con `!help`.")
    else:
        raise error
    
async def load_modules():
    await guide_bot.setup(bot)
    await agend_bot.setup(bot)
    await radio_bot.setup(bot)
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("Bot desconectado.")
        await bot.close()

asyncio.run(load_modules())