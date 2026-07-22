from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://atlas:atlas@localhost:5432/lifeatlas"
    app_title: str = "Life Atlas API"
    debug: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
