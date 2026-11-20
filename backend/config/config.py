from .db_config import DatabaseSettings


class Settings(DatabaseSettings):
    FRONTEND_URL: str = ""
    JWT_SECRET: str = ""
    SQL_ECHO: bool = False


settings = Settings()
