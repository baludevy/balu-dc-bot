from embeds.generic import generic_embed
import discord


class ConfirmationView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.user = self.interaction.user
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message(embed=generic_embed("This command wasn't requested by you."),
                                                    ephemeral=True)
            return False

        return True

    async def on_timeout(self) -> None:
        if self.value is not None:
            return

        for child in self.children:
            if hasattr(child, "disabled"):
                child.disabled = True

        await self.interaction.edit_original_response(embed=generic_embed("You took too long to respond"), view=None)
