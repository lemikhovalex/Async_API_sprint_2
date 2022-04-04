from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field("elasticsearch", env="ELASTIC_HOST")
    es_port: int = Field(9200, env="ELASTIC_PORT")
    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
