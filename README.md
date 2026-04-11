# 🪐 Advad‑Protocol‑Server

Este ecosistema contiene los microservicios y el panel de control oficial del juego, diseñados para empoderar tu proyecto construido en Godot con todo lo necesario en la nube: desde respuestas de inteligencia artificial (LLM proxy) hasta un completo sistema de clasificación para jugadores (Leaderboards).

> ⚠️ **Security note**  
> Todo el sistema depende de Variables de Entorno y Headers privados (`X-App-Token` y `X-Admin-Key`). Mantén tu `.env` a salvo y nunca lo subas a repositorios públicos.

---

## 📁 Estructura del Ecosistema

El proyecto está dividido en tres pilares para mantener limpia la arquitectura de Responsabilidad Única:

```text
.
├── app.py                # 🤖 Servidor AI (FastAPI - Contacto con Gemini LLM)
├── leaderboard_api.py    # 🏆 Servidor Puntuaciones (FastAPI - CRUD Base de Datos)
├── leaderboard-ui/       # 🌐 Frontend visual de Mando (Astro SSR - Cyberpunk UI)
├── package.json          # Orquestador del ecosistema completo
├── requirements.txt      # Dependencias globales de Python
└── .env                  # (Tú lo creas) Variables de configuración secretas
```

---

## 🚀 ¡Levanta Todo el Ecosistema a la Vez!

Para tener una gran experiencia de desarrollo local y dejar todo "listo para usar", puedes aprovechar el orquestador global (Node.js/npm).

### 1. Configuración de Entorno `.env`
Antes de ejecutar nada, crea un archivo `.env` en la raíz del proyecto. Debe contener:

```ini
GEMINI_API_KEY="tu_API_key_real_de_google_gemini"
APP_TOKEN="token_publico_en_juego_para_la_ia"

LEADERBOARD_APP_TOKEN="token_publico_en_juego_para_leaderboard"
ADMIN_SECRET_KEY="clave_privada_acceso_total_del_comandante"
```

### 2. Instala los requerimientos
El comando global se encargará de instalar las dependencias tanto de Python (pip) como de Node.js (Astro). En la raíz ejecuta:

```bash
npm run setup
```

### 3. Activa los servidores en paralelo
¡Magia! Levanta ambos backend en Python y el dashboard en Astro corriendo un solo comando:

```bash
npm run dev
```

Esto iniciará:
- Servidor IA en el puerto **10000**
- Servidor Leaderboard en el puerto **10001**
- El Dashboard interactivo en **http://localhost:4321**

---

## 🧑‍💻 Componente 1: Sistema de Leaderboard 🏆

Este componente gestiona un sistema de Base de Datos local (SQLite) donde los progresos máximos de los jugadores quedan registrados.

- **Datos Independientes:** Los registros se aíslan automáticamente en `/data/phases_log.db` que será ignorado por Git.
- **Rutas (API `localhost:10001`)**:
  - `POST /api/record-phase` (Envía la info al momento de morir).
  - `GET /api/top-pilots` (Lee el Top actual de soldados).
  - `PUT /api/admin/update-phase` (Admin - Alterar Phase).
  - `DELETE /api/admin/delete-pilot` (Admin - Eliminar registro tramposo o test).

### Cómo integrarlo en Godot
```gdscript
var API_URL = "http://localhost:10001/api/record-phase" 
var APP_TOKEN = "tu_LEADERBOARD_APP_TOKEN" 

func submit_score(pilot_name: String, last_phase: int):
    var headers = ["Content-Type: application/json", "X-App-Token: " + APP_TOKEN]
    var json_body = JSON.stringify({"pilot_name": pilot_name, "last_phase": last_phase})
    
    $HTTPRequest.request(API_URL, headers, HTTPClient.METHOD_POST, json_body)
```

### 🌐 Frontend UI (Astro Dashboard)
Ubicado en `leaderboard-ui/`, incluye una vista asombrosa para los jugadores con animaciones, soporte para ver todo al instante, y una página de `/admin` encriptada. Accede escribiendo tu `ADMIN_SECRET_KEY` para visualizar la opción de Purgar.

---

## 🤖 Componente 2: Sistema Inteligencia Artificial (LLM Proxy)

Un endpoint de paso optimizado para darle vida y personalidad a tus personajes utilizando la potencia de **Google Gemini 2.5 Flash**, con rate limits incluídos (anti SPAM) por IP en memoria.

- **Ruta principal:** `POST http://localhost:10000/askai`
- **Protección**: Integración de SlowAPI (10 req/min por IP) e instrucciones rígidas contra prompt injection o jailbreaks.

---

## 💡 Despliegue a Producción

Tú puedes desplegar cada script FastAPI a diferentes servicios gratuitos como **Render.com** o usando **Docker** (el archivo Docker original `DockerFile` viene incluido). Solo añade a Render tus variables del archivo `.env` en sus configuraciones online.

El Frontend en Astro (`/leaderboard-ui`) puede exportarse de forma estática o correrse a través de cualquier hosting compatible en la nube.