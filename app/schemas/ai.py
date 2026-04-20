from pydantic import BaseModel, Field

class AskAIRequest(BaseModel):
    prompt: str = Field(default="", max_length=300)
