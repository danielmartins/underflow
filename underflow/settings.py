from pydantic import BaseSettings


class UnderflowSettings(BaseSettings):
    sck_client_id: str = ""
    sck_client_secret: str = ""
    sck_client_key: str = ""
    sck_redirect_uri: str = "http://localhost:8000/token?"
    tlg_token: str = ""

    class Config:
        env_prefix = "underflow_"
        env_file = ".env"


settings = UnderflowSettings()
