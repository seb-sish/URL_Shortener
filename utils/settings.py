from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class SettingsBase(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8',
                                    #   case_sensitive=False,
                                      env_ignore_empty=True,
                                      extra="ignore")


class DBSettings(SettingsBase):
    model_config = SettingsConfigDict(env_prefix="DB_") 

    HOST: str = Field('localhost')
    PORT: int = Field(5432)
    NAME: str = Field('postgres')
    USER: str = Field('user')
    PASSWORD: str = Field('password')

    @property
    def URL_SQLite(self):
        return f"sqlite+aiosqlite:///./database.db"
    
    @property
    def URL_Postgres(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"
