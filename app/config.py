from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    AGENT_BEARER_TOKEN: str
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str

    class Config:
        env_file = ".env"

settings = Settings()
