from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import sqlite3
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY") 
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def verify_admin(api_key: str = Security(api_key_header)):
    if api_key == ADMIN_SECRET_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Access denied, credentials invalid or missing.")

app = FastAPI(title="ADVAD Central Command API (Secure CRUD)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "phases_log.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phase_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pilot_name TEXT NOT NULL,
            last_phase INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class PhaseSubmit(BaseModel):
    pilot_name: str
    last_phase: int

class PhaseUpdate(BaseModel):
    new_phase: int

@app.post("/api/record-phase")
def record_phase(data: PhaseSubmit):
    if not data.pilot_name or not data.pilot_name.strip():
        data.pilot_name = "Pilot"

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO phase_records (pilot_name, last_phase) VALUES (?, ?)",
            (data.pilot_name, data.last_phase)
        )
        conn.commit()
        conn.close()
        return {"status": "success",
                "message": f"Phase {data.last_phase} recorded for {data.pilot_name}."}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error in the database vault.")

@app.get("/api/top-pilots")
def get_top_pilots():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p1.pilot_name, p1.last_phase as max_phase, MIN(p1.timestamp) as timestamp
            FROM phase_records p1
            INNER JOIN (
                SELECT pilot_name, MAX(last_phase) as max_phase
                FROM phase_records
                GROUP BY pilot_name
            ) p2 ON p1.pilot_name = p2.pilot_name AND p1.last_phase = p2.max_phase
            GROUP BY p1.pilot_name, p1.last_phase
            ORDER BY max_phase DESC, timestamp ASC
            LIMIT 10
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{"pilot": row[0],
                 "phase": row[1], 
                 "timestamp": row[2]} for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail="Read error.")

@app.put("/api/admin/update-phase/{pilot_name}")
def update_pilot_phase(pilot_name: str, data: PhaseUpdate, api_key: str = Depends(verify_admin)):

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE phase_records SET last_phase = ? WHERE pilot_name = ?",
            (data.new_phase, pilot_name)
        )
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="The pilot does not exist.")
            
        return {"status": "success",
                "message": f"Pilot {pilot_name} updated. New phase: {data.new_phase}."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error modifying the record.")

@app.delete("/api/admin/delete-pilot/{pilot_name}")
def ban_pilot(pilot_name: str, api_key: str = Depends(verify_admin)):
    """Borra todo rastro de un piloto de la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM phase_records WHERE pilot_name = ?", (pilot_name,))
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="The pilot does not exist.")
            
        return {"status": "success",
                "message": f"Pilot {pilot_name} deleted from the records."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error to execute the delete command.")

@app.get("/api/admin/all-pilots")
def get_all_pilots(api_key: str = Depends(verify_admin)):
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p1.pilot_name, p1.last_phase as max_phase, MIN(p1.timestamp) as timestamp
            FROM phase_records p1
            INNER JOIN (
                SELECT pilot_name, MAX(last_phase) as max_phase
                FROM phase_records
                GROUP BY pilot_name
            ) p2 ON p1.pilot_name = p2.pilot_name AND p1.last_phase = p2.max_phase
            GROUP BY p1.pilot_name, p1.last_phase
            ORDER BY max_phase DESC, timestamp ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{"pilot": row[0],
                 "phase": row[1], 
                 "timestamp": row[2]} for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail="Read error.")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("LEADERBOARD_PORT", 10001))
    uvicorn.run("leaderboard_api:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")