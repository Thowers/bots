import discord
from discord.ext import commands
from transformers import pipeline, set_seed
from utils.language_handler import load_language, user_languages

class CreativeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("CreativeBot cog loaded.")
        self.generator = pipeline("text-generation", model="distilgpt2")
        set_seed(42)

    @commands.command(name="create_text")
    async def create_text(self, ctx, *, prompt: str = None):
        if ctx.channel.name.lower() != "histories":
            await ctx.send("Este comando solo está disponible en el canal #histories.")
            return

        user_id = ctx.author.id
        lang = user_languages.get(user_id, "en")
        data = load_language(lang)

        if prompt is None:
            prompt = {
                "es": "Escribe aquí una idea creativa para generar contenido.",
                "en": "Write a creative idea to generate content."
            }.get(lang, "Write a creative idea to generate content.")

        await ctx.send(data.get("generando_texto", "🔍 Generating creative content..."))

        try:
            results = self.generator(
                prompt,
                max_length=300,
                min_length=100,
                truncation=True,
                temperature=0.9,
                top_p=0.92,
                repetition_penalty=1.2,
                num_return_sequences=1,
                pad_token_id=50256
            )
            generated_text = results[0]['generated_text']

            if len(generated_text) > 1990:
                generated_text = generated_text[:1990] + "..."

            generated_text = generated_text.replace("“", '"').replace("”", '"').strip()

            await ctx.send(f"**{data.get('resultado', 'Result')}**:\n{generated_text}")
        except Exception as e:
            await ctx.send("There was an error generating the content.")
            print("Error in crear_texto:", e)

async def setup(bot):
    await bot.add_cog(CreativeBot(bot))