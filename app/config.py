from pydantic import BaseSettings

# Set all required env variables here
class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_url: str = ""
    db_port: str
    db_passwort: str
    db_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30


settings = Settings(".env")

setattr(
    settings,
    "db_url",
    f"postgresql://{settings.db_username}:{settings.db_passwort}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
)
