import os
import pytz
import random
import pathlib
import discord
import asyncio
from typing import Optional
from datetime import time
from discord.ext import tasks
from openai import OpenAI


TZ = pytz.timezone("Israel")

SYSTEM_MESSAGE = open(pathlib.Path.cwd() / "system.txt").read()
REPORT_CHANNEL_ID = os.getenv("REPORT_CHANNEL")

intents = discord.Intents.default()
discord_client = discord.Client(intents=intents)
openai_client = OpenAI()


def _gpt_generate_report(breaking: bool = False) -> str:
    if breaking:
        request = "generate breaking news"
    else:
        request = "generate regular daily news"

    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": request
            }
        ]
    )
    return completion.choices[0].message.content


def _generate_breaking_news() -> discord.Embed:
    embed = discord.Embed(
        title=":rotating_light::rotating_light: breaking news :rotating_light::rotating_light:",
        description=_gpt_generate_report(breaking=True),
        color=discord.Color.red()
    )
    embed.set_image(url="https://i.imgur.com/iLW36lG.jpg")
    embed.set_footer(
        text=discord_client.user.name, 
        icon_url=discord_client.user.avatar.url
    )
    return embed


def _generate_daily_news() -> discord.Embed:
    color = [
        discord.Color.blue(), 
        discord.Color.dark_magenta(), 
        discord.Color.blurple(), 
        discord.Color.dark_orange()
    ]
    embed = discord.Embed(
        title=":scroll: daily news :scroll:",
        description=_gpt_generate_report(breaking=False),
        color=random.choice(color)
    )
    embed.set_footer(text="provided by the dailymovich")
    return embed


async def _add_reactions(message: discord.Message) -> None:
    await asyncio.gather(
        message.add_reaction("\U0001F44D"), # thumbs up
        message.add_reaction("\U0001F44E")  # thumbs down
    )


@tasks.loop(hours=8)
async def breaking_news() -> None:
    report_channel = discord_client.get_channel(int(REPORT_CHANNEL_ID))

    if report_channel is None:
        return

    message = await report_channel.send(embed=_generate_breaking_news())
    await _add_reactions(message)

    for channel in report_channel.guild.text_channels:
        if channel.id == report_channel.id:
            continue

        try:
            await channel.send(f":rotating_light::rotating_light::rotating_light: breaking news at <#{REPORT_CHANNEL_ID}> :rotating_light::rotating_light::rotating_light:")
        except discord.errors.Forbidden:
            pass


@tasks.loop(time=[
    time(hour=8, tzinfo=TZ),
    time(hour=15, tzinfo=TZ),
    time(hour=20, tzinfo=TZ),
    time(hour=11, tzinfo=TZ)
])
async def daily_news() -> None:
    report_channel = discord_client.get_channel(int(REPORT_CHANNEL_ID))
    if report_channel is not None:
        message = await report_channel.send(embed=_generate_daily_news())
        await _add_reactions(message)


@discord_client.event
async def on_ready() -> None:
    breaking_news.start()
    daily_news.start()

    await discord_client.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game("🚨🚨🚨")
    )


if __name__ == "__main__":
    discord_client.run(os.getenv("DISCORD_TOKEN"))