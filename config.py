import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Hugging Face Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# News Configuration
RSS_FEEDS = [
    "https://feeds.feedburner.com/eenadutelangananews",
    "https://www.sakshi.com/rss/telangana",
    "https://www.andhrajyothy.com/rss/telangana-news",
    "https://feeds.feedburner.com/tv9telugulatestnews"
]

# App Settings
MAX_CHAT_HISTORY = 100
TTS_LANGUAGE = "te"  # Telugu language code for gTTS
DEFAULT_LANGUAGE = "telugu"
APP_NAME = "Telugu AI Assistant"
VERSION = "1.0.0"

# API Timeouts
REQUEST_TIMEOUT = 10
TTS_TIMEOUT = 15

# Security Settings
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # 1 hour in seconds