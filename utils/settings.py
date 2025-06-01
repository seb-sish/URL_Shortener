from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class SettingsBase(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8',
                                    #   case_sensitive=False,
                                      env_ignore_empty=True,
                                      extra="ignore")


class Settings(SettingsBase):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_") 

    HOST: str = Field('localhost')
    PORT: int = Field(5432)
    DB: str = Field('postgres')
    USER: str = Field('user')
    PASSWORD: str = Field('password')

    DEBUG_SQL: bool = Field(False, description="Enable SQL debug mode")

    @property
    def URL_SQLite(self):
        return f"sqlite+aiosqlite:///./database.db"
    
    @property
    def URL_Postgres(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
    
    @classmethod
    def load(cls) -> "Settings":
        return cls()
    
config = Settings.load()

if __name__ == '__main__':
    print(config)