import discord
import config
from datetime import datetime


def generic_embed(description: str) -> discord.Embed:
    """
    Returns an embed that's used in generic bot replies.
    :param description: Embed description.
    :return:
    """
    embed = discord.Embed(description=f"```\n{description}```",
                          colour=config.color(),
                          timestamp=datetime.now())
    embed.set_footer(text=config.embed_footer())

    return embed
