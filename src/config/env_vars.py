from pydantic_settings import BaseSettings, SettingsConfigDict

from src.globals import PACKAGE_ROOT


class EnvironmentVariables(BaseSettings):
    """
    Load env variables with pydantic.
    Environmental variables would be loaded from a current _session if the .env file is not available
    """
    model_config = SettingsConfigDict(env_file=PACKAGE_ROOT / ".env", env_file_encoding='utf-8')
    DB_URL: str


ENV_VARS = EnvironmentVariables()
DATABASE_URL = "sqlite:///" + ENV_VARS.DB_URL
