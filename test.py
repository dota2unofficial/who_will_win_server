from fastapi import FastAPI
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_PROVIDER: str
    DB_NAME: str
    DB_USER: str

    class Config:
        case_sensitive = True
        env_file = '.env'


settings = Settings()
app = FastAPI()


@app.get("/info")
async def info():
    resp = {
        "DB_PROVIDER": settings.DB_PROVIDER,
        "DB_NAME": settings.DB_NAME,
        "DB_USER": settings.DB_USER,
    }
    print(resp)
    return resp
