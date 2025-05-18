import discord
import wavelink
import config
from discord import app_commands
from discord.ext import commands
from typing import cast
from embeds.music import playing_embed, currently_playing_embed
from embeds.music import in_queue_embed
from embeds.music import queue_embed
from embeds.generic import generic_embed
from views.confirmation import ConfirmationView
from utils import match_space_fuzzy


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.volume: int = 5
        self.muted: bool = False
        self.loop: bool = True
        self.filters = wavelink.Filters
        self.filter_name = "No filter"

    music_group = app_commands.Group(name="music", description="yeah music")

    @music_group.command(name="summon", description="Summon the bot to the vc you are currently in")
    async def summon(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        await self.join_vc(interaction)

        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)

        await response.send_message(embed=generic_embed(f"Connected to #{player.channel.name}"))

    @music_group.command(name="disconnect", description="Disconnect the bot from it's current voice channel")
    async def disconnect(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        channel_name = player.channel.name

        await player.disconnect()

        await response.send_message(embed=generic_embed(f"Disconnected from #{channel_name}"))

    @music_group.command(name="play", description="Play a song")
    @app_commands.describe(query="The title or url of the song you want to play")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            await self.join_vc_with_confirmation(interaction)
            await self.play_music(interaction=interaction, query=query, replace=True)
            return

        await self.play_music(interaction=interaction, query=query)

    @music_group.command(name="stop", description="Stops playing music, it also clears the queue")
    async def stop(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            await response.send_message(embed=generic_embed(f"There isn't any music playing"))
            return

        player.queue.clear()
        await player.stop()

        await response.send_message(embed=generic_embed(f"Stopped playing music"))

    @music_group.command(name="pause", description="Pause music")
    async def pause(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            await response.send_message(embed=generic_embed(f"There isn't any music playing"))
            return

        await player.pause(True)

        await response.send_message(embed=generic_embed(f"Paused"))

    @music_group.command(name="resume", description="Resume playing music")
    async def stop(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            await response.send_message(embed=generic_embed(f"There isn't any music playing"))
            return

        await player.pause(False)

        await response.send_message(embed=generic_embed(f"Resuming"))

    @music_group.command(name="queue", description="Show the tracks that are currently in the queue")
    async def stop(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            await response.send_message(embed=generic_embed(f"There isn't any music playing"))
            return

        if player.queue.is_empty:
            await response.send_message(embed=generic_embed(f"There aren't any tracks in the queue"))
            return

        tracks = list(player.queue)

        await response.send_message(embed=queue_embed("\n".join(
            f"{index}. {track.title} - {track.author}"
            for index, track in enumerate(tracks, start=1)
        )))

    @music_group.command(name="skip", description="Skips to the next track in the queue")
    async def skip(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            await response.send_message(embed=generic_embed(f"There isn't any music playing"))
            return

        if player.queue.is_empty:
            await response.send_message(embed=generic_embed(f"There isn't any music in the queue"))
            return

        await player.skip(force=True)

        track = player.current

        await response.send_message(embeds=[generic_embed(f"Skipping to next track"),
                                            playing_embed(track.author, track.title, track.artwork, track.uri)])

    @music_group.command(name="volume", description="Change the volume of the music")
    @app_commands.describe(volume="Player volume")
    async def volume(self, interaction: discord.Interaction, volume: int) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        if not 1 <= volume <= 100:
            await response.send_message(embed=generic_embed("Volume must be between 1% and 100%"))
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if player:
            await player.set_volume(volume)

        self.volume = volume

        await response.send_message(embed=generic_embed(f"Set volume to: {volume}%"))

    @music_group.command(name="mute", description="Mute music")
    @app_commands.describe(muted="mute")
    async def mute(self, interaction: discord.Interaction, muted: bool) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if muted:
            if player:
                await player.set_volume(0)
                await interaction.guild.change_voice_state(channel=player.channel, self_mute=True, self_deaf=True)

            self.muted = True
            await response.send_message(embed=generic_embed(f"Muted music"))
            return

        if player:
            await player.set_volume(self.volume)
        self.muted = False
        await interaction.guild.change_voice_state(channel=player.channel, self_mute=False, self_deaf=True)
        await response.send_message(embed=generic_embed(f"Unmuted music"))

    @music_group.command(name="filter", description="Set a filter")
    @app_commands.describe(audio_filter="Choose a filter")
    @app_commands.choices(audio_filter=[
        app_commands.Choice(name="Nightcore", value=1),
        app_commands.Choice(name="Ultra-Nightcore", value=2),
        app_commands.Choice(name="Slowed down", value=3),
        app_commands.Choice(name="No filter", value=4),
    ])
    async def filter(self, interaction: discord.Interaction, audio_filter: app_commands.Choice[int]) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            self.filter_name = audio_filter.name
            filters = self.get_filters(audio_filter.name)
            self.filters = filters
            await response.send_message(embed=generic_embed(f"Added filter: {audio_filter.name}"))
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        self.filter_name = audio_filter.name
        filters = self.get_filters(audio_filter.name)
        self.filters = filters
        await player.set_filters(self.filters)

        await response.send_message(embed=generic_embed(f"Added filter: {audio_filter.name}"))

    @music_group.command(name="loop", description="Loop music")
    @app_commands.describe(loop="Should music loop?")
    async def loop(self, interaction: discord.Interaction, loop: bool) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            await self.join_vc_with_confirmation(interaction=interaction)
            await interaction.edit_original_response(embed=generic_embed("Looping on" if loop else "Looping off"),
                                                     view=None)

        self.loop = loop
        player.queue.mode = wavelink.QueueMode.loop if loop else wavelink.QueueMode.normal

        await response.send_message(embed=generic_embed("Looping on" if loop else "Looping off"))

    @music_group.command(name="currently-playing", description="Shows info about the music that's playing currently")
    async def currently_playing(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response  # type: ignore

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            await response.send_message(embed=generic_embed("There isn't any music playing"))
            return

        track = player.current

        embed = currently_playing_embed(track.author, track.title, track.artwork, track.uri, player.position,
                                        track.length, self.volume, self.filter_name)

        await response.send_message(embed=embed[0], file=embed[1])

    @music_group.command(name="remove", description="Remove track from queue")
    @app_commands.describe(track="Track to remove")
    async def remove(self, interaction: discord.Interaction, track: str):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        try:
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        except (AttributeError, TypeError):
            await response.send_message(embed=generic_embed("There isn't any music playing"),
                                                    ephemeral=True)
            return

        if not player or not player.queue:
            await response.send_message(embed=generic_embed("The queue is empty"), ephemeral=True)
            return

        for i, queue_track in enumerate(player.queue):
            if f"{queue_track.title} by {queue_track.author}" == track:
                del player.queue[i]
                await response.send_message(embed=generic_embed(f"Removed track: {track}"))
                return

        await response.send_message(embed=generic_embed("Track not found"), ephemeral=True)

    @remove.autocomplete("track")
    async def track_autocomplete(self, interaction: discord.Interaction, current: str) -> list[
        app_commands.Choice[str]]:

        matches = self.get_track_matches(interaction, current)
        return [app_commands.Choice(name=match, value=match) for match in matches][:25]

    @staticmethod
    def get_track_matches(interaction: discord.Interaction, query: str) -> list[str]:
        matches: list[str] = []

        try:
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        except (AttributeError, TypeError):
            return matches

        if not player or not player.queue:
            return matches

        for track in player.queue:
            track_name = f"{track.title} by {track.author}"

            if (query.lower() in track_name.lower()
                    or track_name.lower() in query.lower()
                    or match_space_fuzzy(track_name, query)
                    or match_space_fuzzy(track_name, query, ".")):
                matches.append(track_name)

        return matches

    async def play_music(self, interaction: discord.Interaction, query: str, replace=False):
        response: discord.InteractionResponse = interaction.response  # type: ignore

        player = cast(wavelink.Player, interaction.guild.voice_client)

        player.autoplay = wavelink.AutoPlayMode.partial

        tracks: wavelink.Search = await wavelink.Playable.search(query)

        if not tracks:
            embed = generic_embed("Couldn't find any tracks with that query.")
            if replace:
                await interaction.edit_original_response(embed=embed, view=None)
            else:
                await response.send_message(embed=embed)
            return

        track = tracks[0]

        if not player.playing:
            embed = playing_embed(track.author, track.title, track.artwork, track.uri, interaction.user.display_name)
            if replace:
                await interaction.edit_original_response(embed=embed, view=None)
            else:
                await response.send_message(embed=embed)

            await player.play(track, volume=0 if self.muted else self.volume)
        else:
            await player.queue.put_wait(track)
            embed = in_queue_embed(track.author, track.title, track.artwork, track.uri, interaction.user.display_name)
            if replace:
                await interaction.edit_original_response(embed=embed, view=None)
            else:
                await response.send_message(embed=embed)

    @staticmethod
    def get_filters(audio_filter: str) -> wavelink.Filters:
        """
        Returns the Wavelink filter settings based on the filter name.
        :param audio_filter: Name of the filter
        :return:
        """
        filters: wavelink.Filters = wavelink.Filters()

        filter_params = config.FILTER_SETTINGS.get(audio_filter, {})
        filters.timescale.set(
            pitch=filter_params.get('pitch', 1),
            speed=filter_params.get('speed', 1),
            rate=1
        )

        return filters

    @staticmethod
    async def join_vc(interaction: discord.Interaction, replace=False):
        response: discord.InteractionResponse = interaction.response  # type: ignore
        try:
            await interaction.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)  # type: ignore
        except AttributeError:
            if replace:
                await interaction.edit_original_response(
                    embed=generic_embed(f"Join a vc before executing this command"))
            else:
                await response.send_message(embed=generic_embed(f"Join a vc before executing this command"))
            return
        except discord.ClientException:
            if replace:
                await interaction.edit_original_response(
                    embed=generic_embed(f"Couldn't join voice chat"))
            else:
                await response.send_message(embed=generic_embed(f"Couldn't join voice chat"))
            return

    async def join_vc_with_confirmation(self, interaction: discord.Interaction):
        response: discord.InteractionResponse = interaction.response  # type: ignore
        view = ConfirmationView(interaction)

        if not interaction.user.voice:
            await response.send_message(embed=generic_embed("You are not in a voice channel."))
            return

        await response.send_message(embed=generic_embed(
            f"I'm not in a voice channel. Do you want me to join #{interaction.user.voice.channel.name}?"),
            view=view)

        if await view.wait():
            return

        if view.value is False:
            await interaction.edit_original_response(embed=generic_embed("Cancelled."), view=None)
            return

        await self.join_vc(interaction, replace=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
