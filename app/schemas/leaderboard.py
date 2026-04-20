from pydantic import BaseModel, Field, field_validator

class PhaseSubmit(BaseModel):
    pilot_name: str = Field(..., max_length=15)
    last_phase: int = Field(..., ge=1)

    @field_validator("pilot_name")
    def check_empty_name(cls, v):
        name = v.strip()
        if not name:
            return "Player"
        return name

class PhaseUpdate(BaseModel):
    new_phase: int = Field(..., ge=1)
