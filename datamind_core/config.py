from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    sf_account:    str = ""
    sf_user:       str = ""
    sf_password:   str = ""
    sf_warehouse:  str = "COMPUTE_WH"
    sf_database:   str = "DATAMIND_DB"
    sf_schema:     str = "PUBLIC"
    sf_role:       str = "SYSADMIN"
    cortex_model:  str = "snowflake-arctic"
    neo4j_uri:     str = "bolt://localhost:7687"
    neo4j_user:    str = "neo4j"
    neo4j_password:str = "datamind_pass"
    knowledge_svc_url: str = "http://localhost:8002"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    class Config:
        env_file = "../.env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()
