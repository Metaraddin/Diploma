from pydantic import BaseSettings


class Settings(BaseSettings):
    authjwt_secret_key: str = "sercet"
    postgres_url: str = "postgresql+psycopg2://postgres:000000@localhost/dpdb"
    timeout: int = 5
    client_secret: str = '0m9cgoidK2yW7tO01yYQRixLdmk2eptGmzgOD7G7'
    client_id: str = '7698'
    redirect_uri: str = 'http://localhost:8000/anilist/auth/callback'

    class Config:
        env_file = '.env'
