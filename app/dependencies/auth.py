from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.config.settings import settings

api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False, scheme_name="AdminKeyHeader")
app_token_header = APIKeyHeader(name="X-App-Token", auto_error=False, scheme_name="AppTokenHeader")

async def verify_admin(api_key: str = Security(api_key_header)):
    if api_key == settings.ADMIN_SECRET_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Access denied, credentials invalid or missing.")

async def verify_app_token(api_key: str = Security(app_token_header)):
    if api_key == settings.APP_TOKEN:
        return api_key
    raise HTTPException(status_code=403, detail="Access denied")
