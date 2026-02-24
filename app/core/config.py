from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Internship API"
    secret_key: str = "change-me-super-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str | None = None
    first_admin_login: str = "admin"
    first_admin_password: str = "pass"

    #Docker (.env)
    db_user: str | None = None
    db_password: str | None = None
    db_name: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.database_url and self.db_user and self.db_password and self.db_name:
            self.database_url = f"postgresql://{self.db_user}:{self.db_password}@db/{self.db_name}"


settings = Settings()