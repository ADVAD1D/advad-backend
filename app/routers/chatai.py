from fastapi import APIRouter, Request, Depends, Security
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai import AskAIRequest
from app.dependencies.auth import verify_app_token
from app.services.chatai_service import ChatAIService

limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
router = APIRouter(tags=["Chat AI"])

@router.get("/")
@router.head("/")
async def home():
    return ChatAIService.get_home_response()

@router.post("/askai")
@limiter.limit("10/minute")
async def ask_ai(request: Request, data: AskAIRequest, api_key: str = Security(verify_app_token)):
    return ChatAIService.ask_ai(data)
