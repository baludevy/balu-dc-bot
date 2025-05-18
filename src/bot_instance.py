from bot import Bot
import config
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
wavelink_uri = os.getenv("WAVELINK_URI")
wavelink_password = os.getenv("WAVELINK_PASSWORD")

bot = Bot(
    command_prefix=config.prefix(),
    wavelink_uri=wavelink_uri,
    wavelink_password=wavelink_password
)


def start_bot():
    if token:
        bot.run(token)
    else:
        print("bitch ahh where token")
