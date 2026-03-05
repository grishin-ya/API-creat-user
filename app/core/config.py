from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Internship API"

    secret_key: str = "change-me-super-secret"
    refresh_secret_key: str = "change-me-refresh-super-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  
    refresh_token_expire_days: int = 7     

    database_url: str | None = None

    first_admin_login: str = "admin"
    first_admin_password: str = "pass"

    db_user: str | None = None
    db_password: str | None = None
    db_name: str | None = None
    db_host: str = "db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def sync_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.db_user and self.db_password and self.db_name:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
        raise ValueError("Database connection not configured")


settings = Settings()