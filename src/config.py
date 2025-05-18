import json

from discord import Status, Color, Game

SYSTEM_COGS = ["dev", "settings"]

botSettings = {}


def read_config() -> object:
    with open('./src/config.json', 'r') as config_file:
        return json.loads(config_file.read())


def write_config(content) -> None:
    with open('./src/config.json', 'w') as config_file:
        config_file.write(content)


def load_config() -> None:
    global botSettings
    config = read_config()
    botSettings = config["botSettings"]


def change_setting(setting: str, value: any):
    config = read_config()
    config["botSettings"][setting] = value
    write_config(json.dumps(config, indent=4))


def bot_instance():
    from bot_instance import bot
    return bot


load_config()


def prefix() -> str:
    return botSettings.get("prefix", ".")


def set_prefix(value: str) -> None:
    config = read_config()
    config["botSettings"]["prefix"] = value
    bot_instance().command_prefix = value
    write_config(json.dumps(config))

    load_config()


def status() -> Status:
    match botSettings.get("status"):
        case "idle":
            return Status.idle
        case "online":
            return Status.online
        case "do_not_disturb":
            return Status.do_not_disturb
    return Status.online


async def set_status(value: str) -> None:
    change_setting("status", value)
    load_config()
    await bot_instance().change_presence(activity=Game(activity()), status=status())


def activity() -> str:
    return botSettings.get("activity")


async def set_activity(value: str) -> None:
    change_setting("activity", value)
    load_config()
    await bot_instance().change_presence(activity=Game(activity()), status=status())


def icon() -> str:
    return botSettings.get("embed_footer_icon")

async def set_icon(value: str) -> None:
    change_setting("embed_footer_icon", value)
    load_config()

def embed_footer() -> str:
    return botSettings.get("embed_footer_text")

async def set_embed_footer(value: str) -> None:
    change_setting("embed_footer_text", value)
    load_config()

def color() -> Color:
    return Color(int(botSettings.get("color", "FFFFFF"), 16))

def get_cogs() -> list[str]:
    return botSettings.get("cogs")

def set_cogs(cogs) -> None:
    for i in range(len(cogs)):
        cogs[i] = cogs[i].removeprefix("cogs.")

    for system_cog in SYSTEM_COGS:
        cogs.remove(system_cog)

    change_setting("cogs", cogs)

FILTER_SETTINGS = {
    "Nightcore": {"pitch": 1.2, "speed": 1.2, "rate": 1},
    "Ultra-Nightcore": {"pitch": 1.3, "speed": 1.4, "rate": 1},
    "Slowed down": {"pitch": 0.8, "speed": 0.8, "rate": 1},
    "No filter": {"pitch": 1, "speed": 1, "rate": 1}
}
