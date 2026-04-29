import json
import sys
import os
from fastapi.openapi.utils import get_openapi

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description="API documentation for the Advad API Server",
    routes=app.routes,
)

with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("OpenAPI schema has been generated and saved to openapi.json")