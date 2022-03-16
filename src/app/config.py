from pydantic import BaseSettings


class Settings(BaseSettings):
    authjwt_secret_key: str = "sercet"
    postgres_url: str = "postgresql+psycopg2://postgres:000000@localhost/dpdb"

    class Config:
        env_file = '.env'
