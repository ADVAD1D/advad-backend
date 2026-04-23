import os
import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    port = settings.PORT
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
