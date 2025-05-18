import os
import discord
import config
import wavelink
from embeds.generic import generic_embed
from discord import app_commands
from discord.ext import commands
from rule34Py import rule34Py


class CommandTree(app_commands.CommandTree):
    bot: "Bot"

    def __init__(
            self,
            client: "Bot",
            *,
            fallback_to_global=True
    ) -> None:
        super().__init__(client=client, fallback_to_global=fallback_to_global)
        self.bot = client

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        print(error)
        await interaction.response.send_message(embed=generic_embed(str(error)))


class Bot(commands.Bot):
    def __init__(self,
                 command_prefix: str,
                 wavelink_uri: str,
                 wavelink_password: str,
                 tree_cls: type[app_commands.CommandTree] = CommandTree,
                 ) -> None:
        self.wavelink_uri = wavelink_uri
        self.wavelink_password = wavelink_password
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all(), tree_cls=tree_cls)

    async def setup_hook(self) -> None:
        await self.load_system_cogs()
        await self.load_cogs_in_config()

        print("Syncing slash command tree...")
        await self.tree.sync()
        print("Done syncing slash command tree")

        await wavelink.Pool.connect(nodes=[wavelink.Node(uri=self.wavelink_uri, password=self.wavelink_password)],
                                    client=self)

        self.activity = discord.Game(config.activity())
        self.status = config.status()

    async def load_cogs_in_config(self) -> None:
        for cog in config.get_cogs():
            await self.load_extension(f"cogs.{cog}")
            print(f"loaded cog: {cog}")

    async def load_system_cogs(self) -> None:
        for system_cog in config.SYSTEM_COGS:
            await self.load_extension(f"cogs.{system_cog}")

    async def load_all_cogs(self) -> int:
        cogs_path = os.path.dirname(__file__) + "/cogs"

        cog_count = 0
        for cog in os.listdir(cogs_path):
            if (not cog.endswith(".py")) or (not os.path.isfile(f"{cogs_path}/{cog}")):
                continue

            cog = cog.removesuffix(".py")

            if f"cogs.{cog}" in self.extensions or cog in config.SYSTEM_COGS:
                continue

            print(f"loaded cog: {cog}")
            cog_count += 1

            await self.load_extension(f"cogs.{cog}")

        return cog_count

    @staticmethod
    async def get_all_cogs() -> list[str]:
        cogs_path = os.path.dirname(__file__) + "/cogs"

        cogs = []
        for cog in os.listdir(cogs_path):
            if (not cog.endswith(".py")) or (not os.path.isfile(f"{cogs_path}/{cog}")):
                continue

            cog = cog.removesuffix(".py")

            if cog in config.SYSTEM_COGS:
                continue

            cogs.append(cog)

        return cogs