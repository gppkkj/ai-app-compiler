from openai import OpenAI
from app.utils.config import settings

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)