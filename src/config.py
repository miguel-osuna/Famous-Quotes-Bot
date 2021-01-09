import os
from os.path import dirname, abspath, join

# File paths
BASE_PROJECT_PATH = dirname(dirname((abspath(__file__))))
LANGUAGES_PATH = join(BASE_PROJECT_PATH, "data", "input", "langs")
COGS_PATH = join(BASE_PROJECT_PATH, "src", "cogs")

# Discord Bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VERSION = os.getenv("VERSION")
SUPPORT_SERVER_INVITE_URL = os.getenv("SUPPORT_SERVER_INVITE_URL")
BOT_INVITE_URL = os.getenv("BOT_INVITE_URL")

# Quotes API
QUOTES_API_URL = os.getenv("QUOTES_API_URL")
QUOTES_API_KEY = os.getenv("QUOTES_API_KEY")
