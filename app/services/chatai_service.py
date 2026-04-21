import logging
import os
from fastapi.responses import JSONResponse
import google.genai as genai
from app.config.settings import settings
from app.schemas.ai import AskAIRequest

logger = logging.getLogger(__name__)

def load_system_instruction():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "chatai_context.md")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading system instruction from file: {e}")
        return "You are a training artificial intelligence for space soldiers of 'The Organization'."

class ChatAIService:
    @staticmethod
    def get_home_response():
        logger.info("Home endpoint accessed")
        return JSONResponse(content="Advad AI Server is running!", status_code=200)

    @staticmethod
    def ask_ai(data: AskAIRequest):
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
                model="gemini-2.5-flash",
                contents=safe_prompt,
                config={
                    "system_instruction": load_system_instruction(),
                    "max_output_tokens": 2048,
                    "temperature": 0.3,
                    "safety_settings": [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE",
                        }
                    ]
                }
            )
            return JSONResponse(content={"response": response.text}, status_code=200)

        except Exception as exc:
            logger.error(f"Internal Server Error: {exc}")
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
