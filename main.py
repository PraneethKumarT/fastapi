from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import engine, Base
from dependencies import templates
from routers import pages, posts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # API routes get JSON; HTML pages get the styled error template.
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors(), "body": exc.body})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "detail": exc.errors(), "body": exc.body},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


app.include_router(pages.router)
app.include_router(posts.router)
app.include_router(users.router)
