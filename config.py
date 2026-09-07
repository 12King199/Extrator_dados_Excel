from dotenv import load_dotenv
import os

load_dotenv()

EXA_API_KEY = os.getenv("EXA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MAX_RESULTS = 5

CACHE_FILE = "cache/cache.json"

OUTPUT_FOLDER = "output"