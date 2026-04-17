from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://user:password@localhost:5432/contacts_db"

    # JWT
    secret_key: str = "change-me-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # SMTP
    mail_username: str = "user@example.com"
    mail_password: str = "password"
    mail_from: str = "user@example.com"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"

    # Cloudinary
    cloudinary_name: str = "cloud-name"
    cloudinary_api_key: str = "api-key"
    cloudinary_api_secret: str = "api-secret"


settings = Settings()
