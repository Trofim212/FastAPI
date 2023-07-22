from pydantic_settings import BaseSettings,SettingsConfigDict
import os

ENV_PATH = os.path.join(os.path.dirname(__file__),'../','.env') 

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH,env_file_encoding='utf-8')
    
    db_connection : str
    db_name : str
    db_host : str
    db_port : str
    db_username : str
    db_password : str
    hash_algorithm : str
    secret_key : str
    access_token_expires_minutes : int
    
settings = Settings()