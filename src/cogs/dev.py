import discord
from discord import app_commands
from discord.ext import commands
import config
from config import SYSTEM_COGS
from embeds.generic import generic_embed
from utils import match_space_fuzzy


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    dev_group = app_commands.Group(name="dev", description="meow")

    @dev_group.command(name="list-cogs", description="List cogs")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(show_all="Show all cogs or only the cogs that are loaded")
    async def list_cogs(self, interaction: discord.Interaction, show_all: bool = True) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        cog_list = await self.bot.get_all_cogs() if show_all else list(self.bot.extensions.keys())

        for i in range(len(cog_list)):
            cog_list[i] = cog_list[i].removeprefix("cogs.")

        if not show_all:
            for cog in SYSTEM_COGS:
                cog_list.remove(cog)

        cogs = "\n".join(cog_list) if len(cog_list) else "No cogs loaded"

        await response.send_message(embed=generic_embed(cogs))

    @dev_group.command(name="reload-all-cogs", description="Reload all loaded cogs")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload_all(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        reloaded_cogs = 0

        for cog in list(self.bot.extensions.keys()):
            await self.bot.reload_extension(cog)
            reloaded_cogs += 1

        await response.send_message(embed=generic_embed(f"Reloaded {reloaded_cogs} cog(s)"))

    @dev_group.command(name="load-all-cogs", description="Load all cogs")
    @app_commands.checks.has_permissions(administrator=True)
    async def load_all(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await response.send_message(embed=generic_embed(
            f"Loaded {await self.bot.load_all_cogs()} cog(s)\nMake sure to sync command tree and reload your client"))

    @dev_group.command(name="load-cog", description="Load a cog")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(cog=[
        app_commands.Choice(name="music", value=1),
        app_commands.Choice(name="nsfw", value=2),
    ])
    @app_commands.describe(update="Update startup cogs so that this cog gets loaded next time you start the bot")
    async def load(self, interaction: discord.Interaction, cog: app_commands.Choice[int], update: bool = False) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await self.bot.load_extension(f"cogs.{cog.name}")

        if not update:
            config.set_cogs(list(self.bot.extensions.keys()))

        await response.send_message(embed=generic_embed(
            f"Loaded {cog.name}\nMake sure to sync command tree and reload your client"))

    @dev_group.command(name="unload-cog", description="Unloads a cog")
    @app_commands.describe(cog="Cog to unload")
    @app_commands.describe(update="Update startup cogs so that this cog doesn't get loaded next time you start the bot")
    async def unload_cog(self, interaction: discord.Interaction, cog: str, update: bool = False) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if f"cogs.{cog}" not in self.bot.extensions:
            return await response.send_message(embed=generic_embed(f"Cog not found: {cog}"))

        await self.bot.unload_extension(f"cogs.{cog}")

        if not update:
            config.set_cogs(list(self.bot.extensions.keys()))

        await response.send_message(embed=generic_embed(f"Unloaded cog: {cog}\nMake sure to sync command tree and reload your client"))

    @unload_cog.autocomplete("cog")
    async def cog_unload_autocomplete(self, interaction: discord.Interaction, current: str) -> list[
        app_commands.Choice[str]]:
        matches = self.get_extension_matches(current)
        return [app_commands.Choice(name=cog, value=cog) for cog in matches][:25]

    @dev_group.command(name="sync-commands", description="Sync the command tree")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync_commands(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await response.send_message(embed=generic_embed(f"Syncing command tree..."))

        await self.bot.tree.sync()

        await interaction.edit_original_response(embed=generic_embed(f"Done syncing command tree"))

    @dev_group.command(name="ping", description="Check the bot's latency to Discord's servers")
    async def ping(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        await response.send_message(embed=generic_embed(f"Pong... {round(self.bot.latency * 1000, 1)}ms"))

    def get_extension_matches(self, query: str) -> list[str]:
        matches: list[str] = []

        for cog in self.bot.extensions:
            if (query.lower() in cog.lower()
                    or cog.lower() in query.lower()
                    or match_space_fuzzy(cog, query)
                    or match_space_fuzzy(cog, query, ".")):
                matches.append(cog.removeprefix("cogs."))

        for system_cog in config.SYSTEM_COGS:
            matches.remove(system_cog)

        return matches


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dev(bot))
