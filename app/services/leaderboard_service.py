from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas.leaderboard import PhaseSubmit, PhaseUpdate
from app.models.phase_record import PhaseRecord

class LeaderboardService:
    @staticmethod
    def normalize_pilot_name(name: str) -> str:
        if not name or not name.strip():
            return "Player"
        return name.strip()

    @staticmethod
    def pilot_name_exists(db: Session, pilot_name: str) -> bool:
        return db.query(PhaseRecord).filter(PhaseRecord.pilot_name == pilot_name).first() is not None

    @staticmethod
    def check_pilot_name(db: Session, pilot_name: str, dev_id: str):
        normalized_name = LeaderboardService.normalize_pilot_name(pilot_name)

        if normalized_name.lower() == "player":
            return {"available": False, "message": "Este indicativo está reservado por el sistema."}
        
        try:
            my_existing_record = db.query(PhaseRecord).filter(
                PhaseRecord.device_id == dev_id,
                PhaseRecord.pilot_name != "Player"
            ).first()
            
            if my_existing_record and my_existing_record.pilot_name != normalized_name and normalized_name != "Player":
                return {"available": False, "message": f"INFRACCIÓN: Su nave ya está registrada como '{my_existing_record.pilot_name}'."}

            record_for_name = db.query(PhaseRecord).filter(PhaseRecord.pilot_name == normalized_name).first()

            if record_for_name is None:
                return {"available": True, "message": "Nombre disponible."}
            elif record_for_name.device_id == dev_id or normalized_name == "Player":
                return {"available": True, "message": f"¡Bienvenido de vuelta, {normalized_name}!"}
            else:
                return {"available": False, "message": "Ese indicativo ya pertenece a otro piloto."}
                
        except Exception as e:
            print(f"Error check_pilot_name: {e}")
            raise HTTPException(status_code=500, detail="Error en la base de datos.")

    @staticmethod
    def get_my_identity(db: Session, dev_id: str):
        if not dev_id:
            return {"pilot_name": None}
            
        try:
            row = db.query(PhaseRecord).filter(
                PhaseRecord.device_id == dev_id,
                PhaseRecord.pilot_name != "Player"
            ).first()
            
            if row:
                return {"pilot_name": row.pilot_name}
            return {"pilot_name": None} 
            
        except Exception:
            return {"pilot_name": None}

    @staticmethod
    def record_phase(db: Session, data: PhaseSubmit, dev_id: str):
        if not dev_id:
            raise HTTPException(status_code=400, detail="Missing Device Identity.")

        data.pilot_name = LeaderboardService.normalize_pilot_name(data.pilot_name)

        try:
            if data.pilot_name != "Player":
                row = db.query(PhaseRecord).filter(PhaseRecord.pilot_name == data.pilot_name).first()
                
                if row and row.device_id != dev_id:
                    raise HTTPException(status_code=409, detail="This name belongs to another pilot.")

            new_record = PhaseRecord(
                pilot_name=data.pilot_name,
                last_phase=data.last_phase,
                device_id=dev_id
            )
            db.add(new_record)
            db.commit()
            return {"status": "success"}
            
        except HTTPException: raise
        except Exception as e:
            db.rollback()
            print(f"Error record_phase: {e}")
            raise HTTPException(status_code=500, detail="DB Error.")

    @staticmethod
    def get_top_pilots(db: Session):
        try:
            # We want the max phase for each pilot, and for ties, the earliest timestamp
            # In PostgreSQL this is often done with DISTINCT ON or subqueries.
            # Using subqueries in SQLAlchemy:
            # subq = session.query(
            #     PhaseRecord.pilot_name,
            #     func.max(PhaseRecord.last_phase).label('max_phase')
            # ).group_by(PhaseRecord.pilot_name).subquery()
            # 
            # q = session.query(
            #     PhaseRecord.pilot_name,
            #     PhaseRecord.last_phase,
            #     func.min(PhaseRecord.timestamp).label('timestamp')
            # ).join(
            #     subq,
            #     (PhaseRecord.pilot_name == subq.c.pilot_name) &
            #     (PhaseRecord.last_phase == subq.c.max_phase)
            # ).group_by(
            #     PhaseRecord.pilot_name, PhaseRecord.last_phase
            # ).order_by(
            #     PhaseRecord.last_phase.desc(),
            #     func.min(PhaseRecord.timestamp).asc()
            # ).limit(10)

            subq = db.query(
                PhaseRecord.pilot_name,
                func.max(PhaseRecord.last_phase).label('max_phase')
            ).group_by(PhaseRecord.pilot_name).subquery()

            rows = db.query(
                PhaseRecord.pilot_name,
                PhaseRecord.last_phase,
                func.min(PhaseRecord.timestamp).label('timestamp')
            ).join(
                subq,
                (PhaseRecord.pilot_name == subq.c.pilot_name) &
                (PhaseRecord.last_phase == subq.c.max_phase)
            ).group_by(
                PhaseRecord.pilot_name,
                PhaseRecord.last_phase
            ).order_by(
                PhaseRecord.last_phase.desc(),
                func.min(PhaseRecord.timestamp).asc()
            ).limit(10).all()

            return [{"pilot": row.pilot_name, "phase": row.last_phase, "timestamp": row.timestamp} for row in rows]
        except Exception as e:
            print(f"Error get_top_pilots: {e}")
            raise HTTPException(status_code=500, detail="Read error.")

    @staticmethod
    def update_pilot_phase(db: Session, pilot_name: str, data: PhaseUpdate):
        try:
            records_updated = db.query(PhaseRecord).filter(PhaseRecord.pilot_name == pilot_name).update({"last_phase": data.new_phase})
            db.commit()

            if records_updated == 0:
                raise HTTPException(status_code=404, detail="The pilot does not exist.")

            return {
                "status": "success",
                "message": f"Pilot {pilot_name} updated. New phase: {data.new_phase}."
            }
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            print(f"Error update_pilot_phase: {e}")
            raise HTTPException(status_code=500, detail="Error modifying the record.")

    @staticmethod
    def ban_pilot(db: Session, pilot_name: str):
        try:
            records_deleted = db.query(PhaseRecord).filter(PhaseRecord.pilot_name == pilot_name).delete()
            db.commit()

            if records_deleted == 0:
                raise HTTPException(status_code=404, detail="The pilot does not exist.")

            return {"status": "success", "message": f"Pilot {pilot_name} deleted from the records."}
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            print(f"Error ban_pilot: {e}")
            raise HTTPException(status_code=500, detail="Error to execute the delete command.")

    @staticmethod
    def get_all_pilots(db: Session):
        try:
            subq = db.query(
                PhaseRecord.pilot_name,
                func.max(PhaseRecord.last_phase).label('max_phase')
            ).group_by(PhaseRecord.pilot_name).subquery()

            rows = db.query(
                PhaseRecord.pilot_name,
                PhaseRecord.last_phase,
                func.min(PhaseRecord.timestamp).label('timestamp')
            ).join(
                subq,
                (PhaseRecord.pilot_name == subq.c.pilot_name) &
                (PhaseRecord.last_phase == subq.c.max_phase)
            ).group_by(
                PhaseRecord.pilot_name,
                PhaseRecord.last_phase
            ).order_by(
                PhaseRecord.last_phase.desc(),
                func.min(PhaseRecord.timestamp).asc()
            ).all()

            return [{"pilot": row.pilot_name, "phase": row.last_phase, "timestamp": row.timestamp} for row in rows]
        except Exception as e:
            print(f"Error get_all_pilots: {e}")
            raise HTTPException(status_code=500, detail="Read error.")
