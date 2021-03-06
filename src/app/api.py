from datetime import timedelta
from time import time

from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

from src.app.tags import tags_metadata
from src.db.database import engine, SessionLocal, DataBase
from src.app.dependencies import get_db, get_settings
from src.routers import user, anilist, manga, staff, genre, product, purchase, test, library, recommendations

app = FastAPI(title="Дипломная работа", version="1.0", openapi_tags=tags_metadata,
              dependencies=[Depends(get_db)])

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(library.router)
app.include_router(manga.router)
app.include_router(genre.router)
app.include_router(staff.router)
app.include_router(product.router)
app.include_router(purchase.router)
app.include_router(anilist.router)
app.include_router(recommendations.router)
app.include_router(test.router)

settings = get_settings()


class JWTSettings(BaseModel):
    authjwt_secret_key: str = settings.authjwt_secret_key
    authjwt_access_token_expires: int = timedelta(hours=2)
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.on_event("startup")
def startup(db: Session = Depends(get_db)):
    start = time()
    connected = False
    while not connected:
        try:
            DataBase.metadata.create_all(bind=engine)
            connected = True
        except OperationalError as e:
            if time() - start > settings.timeout:
                raise e