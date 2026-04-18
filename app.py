import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from routers.ai import router as ai_router, limiter
from routers.leaderboard import router as leaderboard_router

load_dotenv()

app = FastAPI(title="Advad API Server", docs_url="/api/advad-ai/docs", redoc_url="/api/advad-ai/redoc", openapi_url="/api/advad-ai/openapi.json")
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.angelus11.dev",
        "https://angelus11.itch.io",
        "https://advad1d.github.io"
    ],
    allow_origin_regex=r"https://.*\.itch\.zone",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Accept", "X-Forwarded-For", "X-App-Token", "authorization", "X-Admin-Key"],
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
