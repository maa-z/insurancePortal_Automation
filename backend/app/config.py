import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseModel):
    PROJECT_NAME: str = "Insurance Portal AI Agent"
    DATA_PATH: Path = Path(__file__).resolve().parent.parent.parent / "data" / "patients.json"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./insurance_agent.db")
    AI_MODE: str = os.getenv("AI_MODE", "mock").lower()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    PORTAL_BASE_URL: str = os.getenv("PORTAL_BASE_URL", "http://localhost:5173/portal")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")
    MAX_BRANCH_CYCLES_PER_PAGE: int = 15


settings = Settings()
