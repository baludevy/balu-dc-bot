import discord
import config
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO


def playing_embed(author: str, title: str, artwork: str, uri: str, requester: str = "") -> discord.Embed:
    """
    Returns an embed that's used when playing a song.
    :param author: Author to show in the embed
    :param title: Title to show in the embed
    :param artwork: URL of the thumbnail
    :param uri: URL of the song
    :param requester: Display name of the user who requested this song
    :return: discord.Embed
    """
    embed = discord.Embed(title="Now Playing",
                          description=f"```{title} by {author}```",
                          url=uri,
                          colour=config.color(),
                          timestamp=datetime.now())
    embed.set_thumbnail(
        url=artwork)
    embed.set_footer(
        text=f"{config.embed_footer()}" if requester == "" else f"{config.embed_footer()}  •  requested by {requester}")

    return embed


def in_queue_embed(author: str, title: str, artwork: str, uri: str, requester: str) -> discord.Embed:
    """
    Returns an embed that's used when adding a song to the queue.
    :param author: Author to show in the embed
    :param title: Title to show in the embed
    :param artwork: URL of the thumbnail
    :param uri: URL of the song
    :param requester: Display name of the user who requested this song
    :return: discord.Embed
    """
    embed = discord.Embed(title="Added to the queue",
                          description=f"```{title} by {author}```",
                          url=uri,
                          colour=config.color(),
                          timestamp=datetime.now())
    embed.set_thumbnail(
        url=artwork)
    embed.set_footer(text=f"{config.embed_footer()}  •  requested by {requester}")

    return embed


def queue_embed(tracks: str) -> discord.Embed:
    """
    Returns an embed that's used when listing tracks that are currently in the queue.
    :param tracks: Tracks currently in queue.
    :return: discord.Embed
    """
    embed = discord.Embed(title="Tracks in queue",
                          description=f"```{tracks}```",
                          colour=config.color(),
                          timestamp=datetime.now())
    embed.set_footer(text=f"{config.embed_footer()}")

    return embed


def currently_playing_embed(author: str, title: str, artwork: str, uri: str, current_ms: int, total_ms: int,
                            volume: int, audio_filter: str) -> [
    discord.Embed, discord.File]:
    """
    Returns an embed that's used when playing a song with a progress bar.
    :param author: Author to show in the embed
    :param title: Title to show in the embed
    :param artwork: URL of the thumbnail
    :param uri: URL of the song
    :param current_ms: Current position in milliseconds
    :param total_ms: Total duration in milliseconds
    :param volume: Volume
    :param audio_filter: Filter
    :return: discord.Embed object
    """
    embed = discord.Embed(
        title="Currently Playing",
        description=f"```{title} by {author}```",
        url=uri,
        colour=config.color(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=artwork)
    embed.set_footer(
        text=f"{config.embed_footer()}"
    )
    embed.add_field(name="Volume", value=f"```{volume}%```", inline=True)
    embed.add_field(name="Position", value=f"```{ms_to_time_format(current_ms)}```", inline=True)
    embed.add_field(name="Length", value=f"```{ms_to_time_format(total_ms)}```", inline=True)
    embed.add_field(name="Filter", value=f"```{audio_filter}```", inline=True)

    img = create_progress_bar(current_ms, total_ms)
    with BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        file = discord.File(fp=image_binary, filename="progress.png")

    embed.set_image(url="attachment://progress.png")

    return embed, file


def ms_to_time_format(ms: int) -> str:
    """
    Converts milliseconds to a time format (minutes:seconds).
    :param ms: Time in milliseconds
    :return: Formatted time string (minutes:seconds)
    """
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}:{seconds:02}"


def create_progress_bar(current_ms: int, total_ms: int, width: int = 800, height: int = 13,
                        padding: int = 5) -> Image.Image:
    progress = max(0.0, min(1.0, current_ms / total_ms))

    scaling_factor = 4

    scaled_width = (width + 2 * padding) * scaling_factor
    scaled_height = (height + 2 * padding) * scaling_factor
    scaled_padding = padding * scaling_factor

    img = Image.new("RGBA", (scaled_width, scaled_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    progress_width = int(progress * width * scaling_factor)

    radius = (height * scaling_factor) // 2

    if progress_width > 0:
        fill_coords = [
            (scaled_padding, scaled_padding),
            (scaled_padding + progress_width, scaled_padding + height * scaling_factor)
        ]

        draw.rounded_rectangle(
            fill_coords,
            radius=radius,
            fill="#2ECC71"
        )

    outline_width = 3
    outline_color = "#2ECC71"

    outline_coords = [
        (scaled_padding - outline_width, scaled_padding - outline_width),
        (scaled_padding + width * scaling_factor + outline_width,
         scaled_padding + height * scaling_factor + outline_width)
    ]

    draw.rounded_rectangle(
        outline_coords,
        radius=radius + outline_width,
        outline=outline_color,
        width=outline_width * scaling_factor
    )

    final_img = img.resize(
        (width + 2 * padding, height + 2 * padding)
    )

    return final_img
