from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.leaderboard import PhaseSubmit, PhaseUpdate
from app.dependencies.auth import verify_admin
from app.services.leaderboard_service import LeaderboardService
from app.database.connection import get_db

router = APIRouter(tags=["Leaderboard"])

@router.get("/check-name/{pilot_name}")
def check_pilot_name(pilot_name: str, request: Request, db: Session = Depends(get_db)):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.check_pilot_name(db, pilot_name, dev_id)

@router.get("/whoami")
def get_my_identity(request: Request, db: Session = Depends(get_db)):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.get_my_identity(db, dev_id)

@router.post("/record-phase")
def record_phase(data: PhaseSubmit, request: Request, db: Session = Depends(get_db)):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.record_phase(db, data, dev_id)

@router.get("/top-pilots")
def get_top_pilots(db: Session = Depends(get_db)):
    return LeaderboardService.get_top_pilots(db)

@router.put("/admin/update-phase/{pilot_name}")
def update_pilot_phase(pilot_name: str, data: PhaseUpdate, db: Session = Depends(get_db), api_key: str = Depends(verify_admin)):
    return LeaderboardService.update_pilot_phase(db, pilot_name, data)

@router.delete("/admin/delete-pilot/{pilot_name}")
def ban_pilot(pilot_name: str, db: Session = Depends(get_db), api_key: str = Depends(verify_admin)):
    return LeaderboardService.ban_pilot(db, pilot_name)

@router.get("/admin/all-pilots")
def get_all_pilots(db: Session = Depends(get_db), api_key: str = Depends(verify_admin)):
    return LeaderboardService.get_all_pilots(db)
