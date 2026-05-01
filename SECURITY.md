# Security Policy

## 🛡️ Server Security and Encryption

Security is a top priority in this project. We have implemented multiple security layers and a rigorous encryption process to protect the server, the API quota (Gemini), the database, and to prevent vulnerabilities.

### Security Architecture

1. **Environment Variables Encryption (Zero-Disk):**
   - Secrets (API keys, database credentials) are **NEVER** stored in plain text on the disk or in the repository.
   - We use the `cryptography` library (Fernet AES-128-CBC algorithm) to encrypt the `.env` file into an `.env.enc` payload.
   - During server startup, the configuration module (`app/config/settings.py`) decrypts this payload directly into RAM (via `io.StringIO`), avoiding exposing secrets in the server's file system.

2. **Anti-DDoS Mitigation and Rate Limiting:**
   - `slowapi` is used to limit AI requests to **10 per minute per IP**.
   - Real IPs behind cloud reverse proxies (like Render) are resolved using the `X-Forwarded-For` header.

3. **Strict Origin Validation (CORS):**
   - HTTP requests are restricted exclusively to trusted, predefined domains (such as the Astro frontend or the Godot game).

4. **Token Authentication:**
   - We validate every critical request using mandatory tokens (`X-App-Token` for the API and `X-Admin-Key` for management).
   - Any request without a valid token is immediately rejected with a `403 Forbidden` error.

5. **Prompt Injection Protection:**
   - User inputs are safely encapsulated, and the LLM's system instructions are strictly enforced.

### Encryption Workflow (Operations)

To ensure maximum operational security (OPSEC), the entire secret handling process follows a defined workflow:

1. **Key Generation:** `app/security/gen_key.py` is used to create a master key (`secret.key`) locally, which is never uploaded to the repository.
2. **Environment Encryption:** Secrets are written to a temporary `.env` file and run through `app/security/encrypt.py` to generate the secure `.env.enc` file.
3. **Deployment and Loading:** In production (e.g., Render), the master key is passed as a standard environment variable (`SECRET_KEY`), and the `.env.enc` file is loaded as a secret file. The server detects the key, decrypts `.env.enc` in memory, and boots transparently.

---

## 🚨 Vulnerability Reporting

We take security breaches or flaws in the scoring system or AI API consumption very seriously.

If you find a severe vulnerability (such as the ability to bypass token authentication, encryption vulnerabilities, or injections affecting server integrity), **please do not open a public issue**.

Instead, report it directly by sending an email to:
**[angelleonardohern3@gmail.com](mailto:angelleonardohern3@gmail.com)**

Please provide clear details on how to reproduce the vulnerability. We will evaluate and fix the issue as soon as possible.
