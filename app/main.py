import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.routers.chatai import router as ai_router, limiter
from app.routers.leaderboard import router as leaderboard_router

ENVIROMENT = os.getenv("ENVIRONMENT", "production")
is_dev = ENVIROMENT == "development"

app = FastAPI(title="Advad API Server",
            docs_url="/api/advad-ai/docs" if is_dev else None,
            redoc_url="/api/advad-ai/redoc" if is_dev else None,
            openapi_url="/api/advad-ai/openapi.json" if is_dev else None)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.angelus11.dev",
        "https://html-classic.itch.zone",
        "http://localhost:8060",
        "https://angelus11.itch.io",
        "https://advad1d.github.io"
    ],
    allow_origin_regex=r"https://.*\.itch\.zone",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Accept", "X-Forwarded-For", "X-App-Token", "authorization", "X-Admin-Key", "X-Device-ID"]
)

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Has enviado muchos mensajes, espera un momento soldado."
        }
    )

app.include_router(ai_router, prefix="/api/advad-ai")
app.include_router(leaderboard_router, prefix="/api/advad-ai")
