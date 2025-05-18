import discord
from discord import app_commands
from discord.ext import commands
from embeds.generic import generic_embed
from rule34Py import rule34Py

class R34(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.r34 = rule34Py()

    r34_group = app_commands.Group(name="r34", description="sus")

    @r34_group.command(name="get", description="Get random post from r34")
    @app_commands.describe(tag="tag")
    async def get(self, interaction: discord.Interaction, tag: str) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.channel.is_nsfw():
            await response.send_message(embed=generic_embed("You can only run this command in an NSFW channel"))
            return

        await response.send_message(f"{self.r34.random_post([tag]).image}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(R34(bot))
