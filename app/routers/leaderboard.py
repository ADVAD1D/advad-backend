from fastapi import APIRouter, Depends, Request
from app.schemas.leaderboard import PhaseSubmit, PhaseUpdate
from app.dependencies.auth import verify_admin
from app.services.leaderboard_service import LeaderboardService

router = APIRouter(tags=["Leaderboard"])

@router.get("/check-name/{pilot_name}")
def check_pilot_name(pilot_name: str, request: Request):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.check_pilot_name(pilot_name, dev_id)

@router.get("/whoami")
def get_my_identity(request: Request):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.get_my_identity(dev_id)

@router.post("/record-phase")
def record_phase(data: PhaseSubmit, request: Request):
    dev_id = request.headers.get("X-Device-ID")
    return LeaderboardService.record_phase(data, dev_id)

@router.get("/top-pilots")
def get_top_pilots():
    return LeaderboardService.get_top_pilots()

@router.put("/admin/update-phase/{pilot_name}")
def update_pilot_phase(pilot_name: str, data: PhaseUpdate, api_key: str = Depends(verify_admin)):
    return LeaderboardService.update_pilot_phase(pilot_name, data)

@router.delete("/admin/delete-pilot/{pilot_name}")
def ban_pilot(pilot_name: str, api_key: str = Depends(verify_admin)):
    return LeaderboardService.ban_pilot(pilot_name)

@router.get("/admin/all-pilots")
def get_all_pilots(api_key: str = Depends(verify_admin)):
    return LeaderboardService.get_all_pilots()
