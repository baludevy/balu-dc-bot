import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from embeds.generic import generic_embed

class NSFW(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    nsfw_group = app_commands.Group(name="nsfw", description="sus")

    @nsfw_group.command(name="get_image", description="big L")
    @app_commands.describe(category="Choose a category")
    @app_commands.choices(category=[
        app_commands.Choice(name="anal", value=1),
        app_commands.Choice(name="blowjob", value=2),
        app_commands.Choice(name="cum", value=3),
        app_commands.Choice(name="fuck", value=4),
        app_commands.Choice(name="neko", value=5),
        app_commands.Choice(name="pussylick", value=6),
    ])
    async def get_image(self, interaction: discord.Interaction, category: app_commands.Choice[int]):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.channel.is_nsfw():
            await response.send_message(embed=generic_embed("You can only run this command in an NSFW channel"))
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://purrbot.site/api/img/nsfw/{category.name}/gif') as api_response:
                api_response = await api_response.json()

        await response.send_message(api_response["link"], ephemeral=False)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NSFW(bot))
