import discord
from discord import app_commands
from discord.ext import commands
from embeds.generic import generic_embed
import config


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    settings_group = app_commands.Group(name="settings", description="yeah settings")

    @settings_group.command(name="set-prefix", description="Change the bot's prefix")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(prefix="Prefix")
    async def set_activity(self, interaction: discord.Interaction, prefix: str) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        config.set_prefix(prefix)

        await response.send_message(embed=generic_embed(f"Set prefix to: {prefix}"))

    @settings_group.command(name="set-status", description="Change the bot's status")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(status="Status")
    @app_commands.choices(status=[
        app_commands.Choice(name="online", value=1),
        app_commands.Choice(name="idle", value=2),
        app_commands.Choice(name="do_not_disturb", value=3),
    ])
    async def set_activity(self, interaction: discord.Interaction, status: app_commands.Choice[int]) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await config.set_status(status.name)

        await response.send_message(embed=generic_embed(f"Set status to: {status.name}"))

    @settings_group.command(name="set-activity", description="Change the bot's activity text")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(activity="Activity text")
    async def set_activity(self, interaction: discord.Interaction, activity: str) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await config.set_activity(activity)

        await response.send_message(embed=generic_embed(f"Set activity to: {activity}"))

    @settings_group.command(name="set-embed-icon", description="Change the embed footer icon")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(link="Link of the image")
    async def set_activity(self, interaction: discord.Interaction, link: str) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await config.set_icon(link)

        await response.send_message(embed=generic_embed(f"Set embed icon to: {link}"))

    @settings_group.command(name="set-embed-footer", description="Change the embed footer text")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(text="Embed footer text")
    async def set_activity(self, interaction: discord.Interaction, text: str) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await config.set_embed_footer(text)

        await response.send_message(embed=generic_embed(f"Set embed footer text to: {text}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
