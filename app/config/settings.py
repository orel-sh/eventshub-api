from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    redis_url: str = "redis://redis:6379/0"
    elasticsearch_url: str = "http://elasticsearch:9200"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
