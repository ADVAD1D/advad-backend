import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

os.environ["APP_TOKEN"] = "test_super_secret_token"
os.environ["GEMINI_API_KEY"] = "fake_test_api_key"

from main import app

#instancia del cliente de pruebas de fastapi
client = TestClient(app)

#pruebas unitarias

def test_home_endpoint():
    """Prueba que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Advad AI Server is running!"

def test_askai_without_token():
    """Prueba que el endpoint /askai rechace peticiones sin el token correcto."""
    response = client.post("/askai", json={"prompt": "Hola"})
    assert response.status_code == 403
    assert response.json() == {"error": "Access denied"}

def test_askai_wrong_token():
    """Prueba que el endpoint /askai rechace peticiones con un token inválido."""
    headers = {"X-App-Token": "token_equivocado"}
    response = client.post("/askai", headers=headers, json={"prompt": "Hola"})
    assert response.status_code == 403
    assert response.json() == {"error": "Access denied"}

def test_askai_empty_prompt():
    """Prueba el comportamiento cuando el prompt está vacío."""
    headers = {"X-App-Token": "test_super_secret_token"}
    response = client.post("/askai", headers=headers, json={"prompt": ""})
    assert response.status_code == 400
    assert response.json() == {"error": "Prompt is required"}

@patch("main.model.generate_content_async", new_callable=AsyncMock)
def test_askai_success(mock_generate_content):
    """Prueba una petición exitosa simulando la respuesta de la IA."""
    
    class MockGeminiResponse:
        def __init__(self, text):
            self.text = text

    mock_generate_content.return_value = MockGeminiResponse("¡Entendido, soldado! Mantenga la posición.")

    headers = {"X-App-Token": "test_super_secret_token"}
    payload = {"prompt": "Reporte de situación"}


    response = client.post("/askai", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.json() == {"response": "¡Entendido, soldado! Mantenga la posición."}
    
    mock_generate_content.assert_called_once()