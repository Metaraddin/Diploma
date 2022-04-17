from pydantic import BaseSettings


class Settings(BaseSettings):
    authjwt_secret_key: str
    postgres_url: str
    timeout: int
    client_secret: str
    client_id: str
    redirect_uri: str

    class Config:
        env_file = '../.env'
