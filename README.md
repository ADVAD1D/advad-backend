# 🪐 Advad‑AI‑Server

A tiny FastAPI-based API that proxies requests to Google’s Gemini LLM.  
Designed to be embedded in a Godot game so your project can **consume a language‑model API securely and with rate‑limiting**.

> ⚠️ **Security note**  
> The server expects requests to carry an `X‑App‑Token` header; keep this token secret in your game build.  
> The real LLM API key is read from an environment variable on the host machine.

---

## 📁 Repository structure

```
.
├── app.py            # main FastAPI application (uvicorn entrypoint)
├── requirements.txt  # Python dependencies
└── README.md         # this documentation
```

---

## 🧰 Features

- Single endpoint (`/askai`) to send prompts and receive generated text.
- Built‑in rate limiting (10 requests/minute per client IP).
- CORS enabled for cross‑origin calls from your Godot project (FastAPI middleware).
- Simple token‑based authentication to prevent unauthorized use.
- Logging of endpoint hits and errors.
- Configurable model and system instruction for the Gemini API.

---

## 🛡️ Security Changes and Improvements

Multiple security layers have been implemented to protect the server, the Gemini API quota, and mitigate vulnerabilities such as DDoS attacks or endpoint abuse:

- **Anti-DDoS Rate Limiting:** Integration of `slowapi`, limiting requests to **10 per minute per IP** (`@limiter.limit("10/minute")`). It uses `X-Forwarded-For` to resolve real IPs behind proxies.
- **Strict Origin Validation (CORS):** HTTP requests are restricted via `CORSMiddleware` exclusively to trusted domains (`angelus11.dev` and `itch.io` / `itch.zone` domains), blocking unauthorized access from third-party sites.
- **Token Authentication (`X-App-Token`):** Mandatory validation of a secret token on the `/askai` endpoint before processing requests, returning `403 Forbidden` if invalid or missing.
- **Prompt Injection (Jailbreaking) Mitigation:** User inputs are limited and encapsulated (`<<< {raw_prompt} >>>`). System instructions given to Gemini enforce a strict military persona and dictate absolute rejection of out-of-context commands.
- **Secure Exception Handling:** Internal errors (`500`) are controlled via a generic `try-except` block to prevent leaking stack traces or internal information to the client.
- **Structured Data Validation:** Strict use of `pydantic` (`BaseModel`) to validate incoming objects (such as `AskAIRequest`).

---

## 🚀 Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/<your‑username>/advad-ai-server.git
   cd advad-ai-server
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   # or
   source venv/bin/activate     # macOS / Linux
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   Create a `.env` file in the project root or set the variables in your deployment environment.

   ```ini
   GEMINI_API_KEY=your_real_gemini_key
   APP_TOKEN=some_secret_token_for_game
   ```

   - `GEMINI_API_KEY`: API key for Google Generative AI.
   - `APP_TOKEN`: Shared secret that your game will include in requests.

5. **Run locally**

   For development, run the FastAPI app with Uvicorn:

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 10000 --reload
   ```

   The server listens on `0.0.0.0:10000` by default (Render.com uses this port).

---

## 📡 API Endpoints

### `GET /`

Returns a simple health check.

**Response:**

```json
"Advad AI Server is running!"
```

### `POST /askai`

Send a prompt to the LLM.

- **Headers**
  - `Content-Type: application/json`
  - `X-App-Token: <APP_TOKEN>`
- **Body**

  ```json
  {
    "prompt": "Escribe una frase de ánimo para un soldado espacial."
  }
  ```

- **Responses**
  - `200` → `{ "response": "<text from model>" }`
  - `400` → missing prompt
  - `403` → invalid or missing app token
  - `429` → rate limit exceeded
  - `500` → internal error (e.g. missing API key)

> Rate limit: 10 requests per minute per client IP.  
> When exceeded, you receive:

```json
{
  "error": "Rate limit exceeded",
  "message": "Has enviado muchos mensajes, espera un momento soldado."
}
```

---

## 🕹️ Example: Godot Integration

Here’s a minimal GDScript snippet that talks to the server:

```gdscript
var SERVER_URL = "http://localhost:10000/askai"
var APP_TOKEN   = "some_secret_token_for_game"

func ask_ai(prompt: String) -> void:
    var http := HTTPRequest.new()
    add_child(http)
    http.connect("request_completed", self, "_on_response")
    var headers = ["Content-Type: application/json",
                   "X-App-Token: %s" % APP_TOKEN]
    var body = to_json({"prompt": prompt})
    http.request(SERVER_URL, headers, true, HTTPClient.METHOD_POST, body)

func _on_response(result, response_code, headers, body):
    if response_code == 200:
        var data = parse_json(body.get_string_from_utf8())
        print("AI says: ", data["response"])
    else:
        print("Error from server: ", response_code, body.get_string_from_utf8())
```

> ⚠️ **Remember**: keep `APP_TOKEN` private. For a release build, obfuscate or fetch it securely.

---

## 🛠 Deployment

The code is compatible with many PaaS providers (Render.com, Heroku, etc.).  
They usually set environment variables via a dashboard and run Uvicorn or an ASGI server:

```bash
uvicorn app:app --host 0.0.0.0 --port 10000
```

---

## 🐳 Docker

You can build a Docker image to run this server consistently and deploy it to providers that accept container images (e.g. Render.com, Docker Hub). Step-by-step instructions are below.

- **Dockerfile**: the repository already includes `DockerFile` at the project root. If you prefer a minimal `Dockerfile`, this example works (using Uvicorn):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
```

- **Build (local)**: build the image locally (replace `<your-user>`):

```bash
docker build -t <your-user>/advad-ai-server:latest .
```

- **Test locally**: run the image, mapping the port and supplying the required environment variables:

```bash
docker run --rm -e GEMINI_API_KEY="$GEMINI_API_KEY" -e APP_TOKEN="$APP_TOKEN" -p 10000:10000 <your-user>/advad-ai-server:latest
```

- **Tag and push to Docker Hub**:

```bash
docker login
docker tag <your-user>/advad-ai-server:latest <your-user>/advad-ai-server:v1
docker push <your-user>/advad-ai-server:v1
```

## 🚀 Deployment (examples)

Here are two common ways to deploy the image:

- **Render.com (from Dockerfile or Docker Hub image)**
  - Option A — from the repository using `DockerFile`: on Render create a new "Web Service" and select "Docker"; Render will build the image automatically from your `DockerFile` and use port `10000`.
  - Option B — from Docker Hub: publish the image to Docker Hub and on Render create a service "Web Service" → "Docker" → "Private/Official Image" and set `docker.io/<your-user>/advad-ai-server:v1` as the image. Add `GEMINI_API_KEY` and `APP_TOKEN` in the Environment Variables. Ensure port `10000` is configured if Render requests it.

- **Simple deployment using Docker Hub + any Docker host**
  - Push the image to Docker Hub (see commands above).
  - On the host/server run:

```bash
docker pull <your-user>/advad-ai-server:v1
docker run -d --restart unless-stopped -p 10000:10000 \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" -e APP_TOKEN="$APP_TOKEN" \
  <your-user>/advad-ai-server:v1
```

---

## 📦 `requirements.txt`

```txt
fastapi
uvicorn[standard]
slowapi
python-dotenv
google-generativeai
```

---

## 📝 Customization

- **Change model or instruction**  
  Edit the `model = genai.GenerativeModel(...)` block in `app.py`.

- **Adjust rate limiting**  
  Modify the rate limit decorator or configuration in the FastAPI app (e.g. `slowapi` rules).

- **Logging level**  
  Change `logging.basicConfig(level=logging.INFO)` to `DEBUG` for more verbosity.

---

## **Changes in app.py**

- **Scope**: Changes made in the main script [app.py](app.py). The following bullets summarize the functional and configuration changes implemented there.
- **Auth**: `POST /askai` requires the `X-App-Token` header and compares it against the `APP_TOKEN` environment variable; an invalid or missing token returns a `403` JSON error.
- **Rate limiting**: Uses `slowapi.Limiter` with a custom `get_real_ip` key function that respects `X-Forwarded-For` (so it works behind proxies). The limiter uses in-memory storage and the `/askai` route is decorated with `@limiter.limit("10/minute")` (per client IP).
- **Gemini integration**: Loads `GEMINI_API_KEY` from the environment (via `python-dotenv`) and configures `google.generativeai`. The server instantiates a `gemini-2.5-flash` model with a strict `system_instruction` enforcing language matching, a military persona, and a special code flow. `generation_config` is set (`max_output_tokens=2048`, `temperature=0.3`) and custom `safety_settings` are applied.
- **Prompt handling & generation**: Incoming prompts are validated and wrapped into a Spanish "Comando del soldado..." template before being sent to the model via the asynchronous call `model.generate_content_async()`. The returned `response.text` is sent back in the JSON `response` field.
- **Endpoints**: Adds a health endpoint (`GET`/`HEAD` `/`) that returns a JSON message and a `POST /askai` endpoint that enforces auth, rate limits, prompt validation, and calls the Gemini model.
- **Error handling & logging**: Adds an exception handler for `RateLimitExceeded` that returns a `429` with a Spanish-friendly message, returns `400` for missing prompts, `500` when the API key is missing or on internal errors, and configures `logging` at the `INFO` level.
- **CORS & runtime**: Adds permissive CORS middleware, loads environment variables with `dotenv`, and uses `uvicorn.run` when executed directly (reads `PORT`, defaults to `10000`).
- **Other notes**: Implements a helper `get_real_ip`, prints a warning when `GEMINI_API_KEY` is not set (instead of raising), includes example curl/PowerShell snippets in comments, and keeps rate limit data in memory for simplicity.

---

## 🧪 Unit Tests (`test_mock.py`)

The project includes a suite of unit tests using `pytest`, `fastapi.testclient`, and `unittest.mock` to verify the functionality of the API without making real calls to the Gemini LLM.

- **Environment Setup**: The test suite initializes fake environment variables (`APP_TOKEN` and `GEMINI_API_KEY`) to ensure tests run in a controlled environment and do not depend on real credentials.
- **Home Endpoint (`test_home_endpoint`)**: Verifies that a `GET` request to the root URL (`/`) returns a `200 OK` status and the expected "Advad AI Server is running!" health check message.
- **Authentication (Missing Token) (`test_askai_without_token`)**: Ensures that a `POST` request to `/askai` without the `X-App-Token` header is rejected with a `403 Forbidden` status and an "Access denied" error.
- **Authentication (Invalid Token) (`test_askai_wrong_token`)**: Checks that a `POST` request to `/askai` with an incorrect `X-App-Token` header is also rejected with a `403 Forbidden` status.
- **Validation (Empty Prompt) (`test_askai_empty_prompt`)**: Validates that sending an empty prompt string to `/askai` results in a `400 Bad Request` status and a "Prompt is required" error.
- **Successful AI Request Simulation (`test_askai_success`)**: Tests a valid request to `/askai` by mocking the asynchronous call to the Gemini API (`generate_content_async`). It simulates a successful AI response and asserts that the endpoint returns a `200 OK` status with the correct simulated text, verifying that the internal AI generation method was called exactly once.

---

## 🧾 License & Contribution

Feel free to fork, modify, or integrate this microserver into your own projects.  
Contributions and issues are welcome.

---

> ✅ Ready for use with your Godot game.  
> 💡 Bonus: you can expand this server with new endpoints—dialogue history, user IDs, etc., as your AI-driven gameplay grows.