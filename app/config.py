from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_env: str = "production"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_secret_key: str = "CHANGE_ME"
    dashboard_password: str = "CHANGE_ME"
    cookie_secure: bool = True
    session_max_age: int = 43200
    data_dir: Path = Path("/data/facebook-ai")
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "nvidia/nemotron-3-ultra-550b-a55b"
    nvidia_timeout_seconds: int = 120
    max_prompt_chars: int = 8000

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    return settings
