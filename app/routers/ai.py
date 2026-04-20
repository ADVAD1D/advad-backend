import logging
from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import google.genai as genai
from app.config.settings import settings
from app.schemas.ai import AskAIRequest

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
router = APIRouter(tags=["AI"])

@router.get("/")
@router.head("/")
async def home():
    logger.info("Home endpoint accessed")
    return JSONResponse(content="Advad AI Server is running!", status_code=200)

@router.post("/askai")
@limiter.limit("10/minute")
async def ask_ai(request: Request, data: AskAIRequest, x_app_token: str = Header(default=None, alias="X-App-Token")):
    if x_app_token != settings.APP_TOKEN:
        return JSONResponse(content={"error": "Access denied"}, status_code=403)

    if not settings.GEMINI_API_KEY:
        return JSONResponse(content={"error": "GEMINI_API_KEY not set"}, status_code=500)

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    raw_prompt = data.prompt.replace("<", "").replace(">", "")
    if not raw_prompt:
        return JSONResponse(content={"error": "Prompt is required"}, status_code=400)

    safe_prompt = f"""
    Incoming command from The Organization soldier::
    <<<{raw_prompt}>>>

    Evaluate the command and respond maintaining your strict military identity. Remember to reply in the exact same language the soldier used inside the <<< >>> brackets..
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=safe_prompt
        )
        return JSONResponse(content={"response": response.text}, status_code=200)

    except Exception as exc:
        logger.error(f"Internal Server Error: {exc}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
