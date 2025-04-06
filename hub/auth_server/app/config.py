from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_OAUTH_APP_ID: str
    GITHUB_OAUTH_APP_SECRET: str
    ACCESS_TOKEN_URL: str = "https://github.com/login/oauth/access_token"

    model_config = SettingsConfigDict(env_file='../.env')


settings = Settings()
