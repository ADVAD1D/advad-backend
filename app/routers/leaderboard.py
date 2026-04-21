import os
from app.schemas.leaderboard import PhaseSubmit, PhaseUpdate
from app.dependencies.auth import verify_admin
from fastapi import APIRouter, HTTPException, Depends, Request

from app.config.settings import settings
router = APIRouter(tags=["Leaderboard"])
from app.database.connection import get_db_connection

def normalize_pilot_name(name: str) -> str:
    if not name or not name.strip():
        return "Player"
    return name.strip()

def pilot_name_exists(cursor, pilot_name: str) -> bool:
    cursor.execute("SELECT 1 FROM phase_records WHERE pilot_name = %s LIMIT 1", (pilot_name,))
    return cursor.fetchone() is not None

@router.get("/check-name/{pilot_name}")
def check_pilot_name(pilot_name: str, request: Request):
    dev_id = request.headers.get("X-Device-ID")
    normalized_name = normalize_pilot_name(pilot_name)

    if normalized_name.lower() == "player":
        return {"available": False, "message": "Este indicativo está reservado por el sistema."}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT pilot_name FROM phase_records WHERE device_id = %s AND pilot_name != 'Player' LIMIT 1", (dev_id,))
        my_existing_name = cursor.fetchone()
        
        if my_existing_name and my_existing_name[0] != normalized_name and normalized_name != "Player":
            conn.close()
            return {"available": False, "message": f"INFRACCIÓN: Su nave ya está registrada como '{my_existing_name[0]}'."}

        cursor.execute("SELECT device_id FROM phase_records WHERE pilot_name = %s LIMIT 1", (normalized_name,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return {"available": True, "message": "Nombre disponible."}
        elif row[0] == dev_id or normalized_name == "Player":
            return {"available": True, "message": f"¡Bienvenido de vuelta, {normalized_name}!"}
        else:
            return {"available": False, "message": "Ese indicativo ya pertenece a otro piloto."}
            
    except Exception:
        raise HTTPException(status_code=500, detail="Error en la base de datos.")
    
@router.get("/whoami")
def get_my_identity(request: Request):
    dev_id = request.headers.get("X-Device-ID")
    if not dev_id:
        return {"pilot_name": None}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT pilot_name FROM phase_records WHERE device_id = %s AND pilot_name != 'Player' LIMIT 1", 
            (dev_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {"pilot_name": row[0]}
        return {"pilot_name": None} 
        
    except Exception:
        return {"pilot_name": None}

@router.post("/record-phase")
def record_phase(data: PhaseSubmit, request: Request):
    dev_id = request.headers.get("X-Device-ID")
    if not dev_id:
        raise HTTPException(status_code=400, detail="Missing Device Identity.")

    data.pilot_name = normalize_pilot_name(data.pilot_name)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if data.pilot_name != "Player":
            cursor.execute(
                "SELECT device_id FROM phase_records WHERE pilot_name = %s LIMIT 1", 
                (data.pilot_name,)
            )
            row = cursor.fetchone()
            
            if row and row[0] != dev_id:
                conn.close()
                raise HTTPException(status_code=409, detail="This name belongs to another pilot.")

        cursor.execute(
            "INSERT INTO phase_records (pilot_name, last_phase, device_id) VALUES (%s, %s, %s)",
            (data.pilot_name, data.last_phase, dev_id)
        )
        conn.commit()
        conn.close()
        return {"status": "success"}
        
    except HTTPException: raise
    except Exception: raise HTTPException(status_code=500, detail="DB Error.")

@router.get("/top-pilots")
def get_top_pilots():
    try:
        conn = get_db_connection()
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
        return [{"pilot": row[0], "phase": row[1], "timestamp": row[2]} for row in rows]
    except Exception:
        raise HTTPException(status_code=500, detail="Read error.")

@router.put("/admin/update-phase/{pilot_name}")
def update_pilot_phase(pilot_name: str, data: PhaseUpdate, api_key: str = Depends(verify_admin)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE phase_records SET last_phase = %s WHERE pilot_name = %s",
            (data.new_phase, pilot_name)
        )
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()

        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="The pilot does not exist.")

        return {
            "status": "success",
            "message": f"Pilot {pilot_name} updated. New phase: {data.new_phase}."
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error modifying the record.")

@router.delete("/admin/delete-pilot/{pilot_name}")
def ban_pilot(pilot_name: str, api_key: str = Depends(verify_admin)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM phase_records WHERE pilot_name = %s", (pilot_name,))
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()

        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="The pilot does not exist.")

        return {"status": "success", "message": f"Pilot {pilot_name} deleted from the records."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error to execute the delete command.")

@router.get("/admin/all-pilots")
def get_all_pilots(api_key: str = Depends(verify_admin)):
    try:
        conn = get_db_connection()
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
        return [{"pilot": row[0], "phase": row[1], "timestamp": row[2]} for row in rows]
    except Exception:
        raise HTTPException(status_code=500, detail="Read error.")
