import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from utils.language_handler import load_language, user_languages
from utils.mongo import database

def dm_only(ctx):
    return isinstance(ctx.channel, discord.DMChannel)

class AgendBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AgendBot cog loaded")
        self.events_collection = database.get_collection("Eventos")
        self.check_reminders.start()
        self.cleanup_old_events.start()

    @commands.command(name="add_event")
    async def add_event(self, ctx):
        if not dm_only(ctx):
            await ctx.author.send("Please use commands in DM.")
            return

        user_id = ctx.author.id
        lang = user_languages.get(user_id, "en")
        data = load_language(lang)

        msg = {
            "es": "Por favor envía el evento en el siguiente formato:\n`DD/MM/YYYY HH:MM(Formato de 24H) Descripción | minutos_para_recordar`",
            "en": "Please send the event in the following format:\n`DD/MM/YYYY HH:MM(24-H Format) Description | reminder_minutes`"
        }.get(lang, data.get("formato_evento", ""))

        await ctx.send(msg)

        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        try:
            user_msg = await self.bot.wait_for("message", check=check, timeout=120.0)
            content = user_msg.content

            if "|" not in content:
                await ctx.send(data.get("formato_invalido", "Invalid format. Use: `DD/MM/YYYY HH:MM Description | reminder_minutes`"))
                return

            datetime_part, reminder_part = content.split("|", 1)
            parts = datetime_part.strip().split(" ", 2)

            if len(parts) < 3:
                await ctx.send(data.get("formato_invalido", "Invalid format. Use: `DD/MM/YYYY HH:MM Description | reminder_minutes`"))
                return

            date_str, time_str, description = parts
            reminder_minutes = int(reminder_part.strip())

            dt = datetime.strptime(f'{date_str} {time_str}', "%d/%m/%Y %H:%M")
            reminder_time = dt - timedelta(minutes=reminder_minutes)

            if reminder_time < datetime.now():
                await ctx.send(data.get("tiempo_recordatorio_pasado", "Reminder time is in the past. Please try again with more time."))
                return

            event = {
                "user_id": user_id,
                "username": str(ctx.author),
                "datetime": dt,
                "remind_at": reminder_time,
                "description": description,
                "reminder_minutes": reminder_minutes,
                "reminded": False,
                "created_at": datetime.now()
            }

            result = self.events_collection.insert_one(event)
            print(f"✅ Evento guardado: {result.inserted_id}")
            print(f"🔔 Se enviará recordatorio a las: {reminder_time.strftime('%d/%m/%Y %H:%M')}")

            response = data.get("evento_agregado", "Event added") + f": {dt.strftime('%d/%m/%Y %H:%M')} - {description}\n"
            response += data.get("recordatorio_programado", "Reminder will be sent at") + f" {reminder_time.strftime('%d/%m/%Y %H:%M')}"
            await ctx.send(response)

        except Exception as e:
            await ctx.send(data.get("error_evento", "There was an error creating the event."))
            print("❌ Error en add_event:", e)

    @commands.command(name="list_events")
    async def list_events(self, ctx):
        if not dm_only(ctx):
            await ctx.author.send("Please use commands in DM.")
            return

        user_id = ctx.author.id
        lang = user_languages.get(user_id, "en")
        data = load_language(lang)
        events_cursor = self.events_collection.find({"user_id": user_id}).sort("datetime", 1)
        events = list(events_cursor)

        if not events:
            await ctx.send(data.get("sin_eventos", "You have no scheduled events."))
            return

        response = data.get("tus_eventos", "**Your events:**\n")
        for event in events:
            dt = event["datetime"]
            description = event["description"]
            remind_at = event.get("remind_at")
            response += f"🗓️ {dt.strftime('%d/%m/%Y %H:%M')} - {description} | 🔔 {remind_at.strftime('%H:%M %d/%m') if remind_at else 'N/A'}\n"

        await ctx.send(response)

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        now = datetime.now()
        upcoming_events = self.events_collection.find({
            "remind_at": {"$lte": now},
            "reminded": False
        })

        for event in upcoming_events:
            user_id = event["user_id"]
            user = self.bot.get_user(user_id)
            if not user:
                continue

            lang = user_languages.get(user_id, "en")
            data = load_language(lang)

            reminder_msg = {
                "es": f"⏰ ¡Recordatorio de evento!\n**{event['description']}** a las {event['datetime'].strftime('%d/%m/%Y %H:%M')}",
                "en": f"⏰ Event Reminder!\n**{event['description']}** at {event['datetime'].strftime('%d/%m/%Y %H:%M')}"
            }.get(lang, "⏰ Event Reminder!")

            try:
                await user.send(reminder_msg)
                self.events_collection.update_one({"_id": event["_id"]}, {"$set": {"reminded": True}})
                print(f"🔔 Recordatorio enviado a {user} - {event['description']}")
            except Exception as e:
                print(f"❌ No se pudo enviar recordatorio a {user_id}: {e}")

    @commands.command(name="bot_time")
    async def time(self, ctx):
        now = datetime.now()
        await ctx.send(f"🕒 Hora actual del bot: {now.strftime('%d/%m/%Y %H:%M:%S')}")

    @tasks.loop(minutes=10)
    async def cleanup_old_events(self):
        now = datetime.now()
        result = self.events_collection.delete_many({"datetime": {"$lt": now}})
        if result.deleted_count > 0:
            print(f"🧹 Limpieza: {result.deleted_count} evento(s) eliminados por estar en el pasado.")

async def setup(bot):
    await bot.add_cog(AgendBot(bot))