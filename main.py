from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
