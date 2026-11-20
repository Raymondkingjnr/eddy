from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.users.users import auth_backend, fastapi_users
from schemas import UserCreate, UserRead, UserUpdate
from contextlib import asynccontextmanager
from config.db import engine
from config.config import settings
from api.users.router import router as users_router
from api.stats.router import router as stats_router
from api.lessons.router import router as lessons_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

frontend_origins = [
    origin.strip().rstrip("/")
    for origin in settings.FRONTEND_URL.split(",")
    if origin.strip()
]
if frontend_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=frontend_origins,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

app.router.include_router(fastapi_users.get_auth_router(
    auth_backend), prefix="/auth/jwt", tags=["auth"])

app.router.include_router(fastapi_users.get_register_router(
    UserRead, UserCreate), prefix="/auth", tags=["auth"])

app.router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])

app.router.include_router(fastapi_users.get_verify_router(
    UserRead), prefix="/auth", tags=["auth"])

app.include_router(users_router)

app.router.include_router(fastapi_users.get_users_router(
    UserRead, UserUpdate), prefix="/users", tags=["users"])

app.include_router(stats_router)
app.include_router(lessons_router)
