from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from core.config import STATIC_DIR, STATIC_MOUNT_PATH, settings
from core.models import Base, db_helper
from admin.api.routes import router as admin_router
from api.routes import router as client_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Основное приложение
app = FastAPI(
    title="Main API",
    version="1.0",
    docs_url="/docs",  # Отключаем документацию на корне, если она не нужна
    lifespan=lifespan
)

# Админское приложение
admin_app = FastAPI(
    title="Admin API",
    version="1.0",
    docs_url="/docs",  # Документация будет доступна по /admin/docs
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Подключение роутеров
admin_app.include_router(router=admin_router, prefix="/api/v1")  # Префикс внутри admin_app
app.include_router(router=client_router, prefix="/api/v1")

# Монтирование приложений на разные пути
app.mount(STATIC_MOUNT_PATH, StaticFiles(directory=STATIC_DIR), name="images")
app.mount("/admin", admin_app)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
