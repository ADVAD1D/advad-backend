# 🪐 Advad‑AI‑Server

A tiny FastAPI-based API that proxies requests to Google’s Gemini LLM and manages a real-time game leaderboard.  
Designed to be embedded in a Godot game so your project can **consume a language‑model API securely and with rate‑limiting**, while also tracking player scores securely.

> ⚠️ **Security note**  
> The server expects requests to carry `X‑App‑Token` / `X-Admin-Key` headers; keep these tokens secret.  
> The real LLM API key is read from an environment variable on the host machine.

---

## 📁 Repository structure

```text
.
├── app.py                # main FastAPI application (AI interaction)
├── leaderboard_api.py    # FastAPI application (CRUD for leaderboards)
├── package.json          # Concurrent dev script manager
├── requirements.txt      # Python dependencies
└── README.md             # this documentation
```

---

## 🧰 Features

- Single endpoint (`/askai`) to send prompts and receive generated text.
- Separate API (`leaderboard_api.py`) for managing a SQLite leaderboard database.
- Built‑in rate limiting (10 requests/minute per client IP for the AI).
- CORS enabled for cross‑origin calls from your Godot project or Astro Frontend.
- Simple token‑based authentication to prevent unauthorized use.

---

## 🛡️ Security Changes and Improvements

Multiple security layers have been implemented to protect the server, the Gemini API quota, and mitigate vulnerabilities such as DDoS attacks or endpoint abuse:

- **Anti-DDoS Rate Limiting:** Integration of `slowapi`, limiting requests to **10 per minute per IP** (`@limiter.limit("10/minute")`). It uses `X-Forwarded-For` to resolve real IPs behind proxies.
- **Strict Origin Validation (CORS):** HTTP requests are restricted via `CORSMiddleware` exclusively to trusted domains (`angelus11.dev` and `itch.io` / `itch.zone` domains), blocking unauthorized access from third-party sites.
- **Token Authentication (`X-App-Token` / `X-Admin-Key`):** Mandatory validation of a secret token on the endpoints before processing requests, returning `403 Forbidden` if invalid or missing.
- **Prompt Injection (Jailbreaking) Mitigation:** User inputs are limited and encapsulated (`<<< {raw_prompt} >>>`). System instructions given to Gemini enforce a strict military persona and dictate absolute rejection of out-of-context commands.
- **Secure Exception Handling:** Internal errors (`500`) are controlled via a generic `try-except` block to prevent leaking stack traces or internal information to the client.
- **Structured Data Validation:** Strict use of `pydantic` (`BaseModel`) to validate incoming objects.

---

## 🚀 Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/<your‑username>/advad-backend.git
   cd advad-backend
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   # or
   source venv/bin/activate     # macOS / Linux
   ```

3. **Install dependencies**:

   Using NPM wrapper (installs Python dependencies automatically):
   ```bash
   npm run setup
   ```
   *Alternatively, plain python:* `pip install -r requirements.txt`

4. **Configure environment variables**:

   Create a `.env` file in the project root or set the variables in your deployment environment.

   ```ini
   GEMINI_API_KEY=your_real_gemini_key
   APP_TOKEN=some_secret_token_for_ai
   
   LEADERBOARD_APP_TOKEN=some_secret_token_for_game_scores
   ADMIN_SECRET_KEY=some_secret_token_for_admin_actions
   ```

5. **Run locally**

   For development, run both FastAPI apps simultaneously using the NPM wrapper:

   ```bash
   npm run dev
   ```

   - AI Server listens on `0.0.0.0:10000`
   - Leaderboard Server listens on `0.0.0.0:10001`

---

## 📡 Leaderboard API Endpoints (Port 10001)

### `POST /api/record-phase`
Open (requires body data) endpoint to submit a player's reached phase.
- **Body**: `{"pilot_name": "Ghost", "last_phase": 15}`

### `GET /api/top-pilots`
Public endpoint returning the top 10 grouped high scrores.

### `DELETE /api/admin/delete-pilot/{pilot_name}`
Requires `X-Admin-Key` header. Purges a specific pilot from the database.

---

## 📡 AI API Endpoints (Port 10000)

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

## 🕹️ Example: Godot Integration (Leaderboards)

Here’s a snippet demonstrating how to post a score:

```gdscript
var API_URL = "http://localhost:10001/api/record-phase" 

func submit_score(pilot_name: String, last_phase: int):
    var headers = ["Content-Type: application/json"]
    var json_body = JSON.stringify({
        "pilot_name": pilot_name,
        "last_phase": last_phase
    })
    
    var http := HTTPRequest.new()
    add_child(http)
    http.request(API_URL, headers, HTTPClient.METHOD_POST, json_body)
```

---

## 🛠 Deployment

The code is compatible with many PaaS providers (Render.com, Heroku, etc.).  
They usually set environment variables via a dashboard and run Uvicorn or an ASGI server:

```bash
uvicorn app:app --host 0.0.0.0 --port 10000
uvicorn leaderboard_api:app --host 0.0.0.0 --port 10001
```

---

## 🐳 Docker

You can build a Docker image to run this server consistently and deploy it to providers that accept container images (e.g. Render.com, Docker Hub).

- **Dockerfile**: the repository already includes `DockerFile` at the project root for the AI Server.

---

## 📝 Customization

- **Change model or instruction**  
  Edit the `model = genai.GenerativeModel(...)` block in `app.py`.

- **Adjust rate limiting**  
  Modify the rate limit decorator or configuration in the FastAPI app (e.g. `slowapi` rules).

---

## 🧪 Unit Tests (`test_mock.py`)

The project includes a suite of unit tests using `pytest`, `fastapi.testclient`, and `unittest.mock` to verify the functionality of the API without making real calls to the Gemini LLM. Includes validation for missing tokens, empty prompts, and success requests mockings.

---

## 🧾 License & Contribution

Feel free to fork, modify, or integrate this microserver into your own projects.  
Contributions and issues are welcome.

---

> ✅ Ready for use with your Godot game.  
> 💡 Bonus: you can expand this server with new endpoints—dialogue history, user IDs, etc., as your AI-driven gameplay grows.