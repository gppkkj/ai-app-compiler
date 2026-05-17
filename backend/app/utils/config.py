from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()

print("Loaded Key:", settings.OPENAI_API_KEY)