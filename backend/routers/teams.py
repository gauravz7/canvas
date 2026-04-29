from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, CurrentUser
from models import Team, TeamMember
from pydantic import BaseModel
import uuid
import string
import random

router = APIRouter()

class CreateTeamRequest(BaseModel):
    name: str

class JoinTeamRequest(BaseModel):
    join_code: str

def _generate_join_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

@router.post("/create")
def create_team(req: CreateTeamRequest, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    team = Team(
        id=str(uuid.uuid4()),
        name=req.name,
        join_code=_generate_join_code(),
        created_by=current_user.uid
    )
    db.add(team)

    member = TeamMember(
        team_id=team.id,
        user_id=current_user.uid,
        user_email=current_user.email,
        user_name=current_user.name,
        role="owner"
    )
    db.add(member)
    db.commit()

    return {"id": team.id, "name": team.name, "join_code": team.join_code, "role": "owner"}

@router.post("/join")
def join_team(req: JoinTeamRequest, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.join_code == req.join_code).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    existing = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.uid).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already a member")

    member = TeamMember(
        team_id=team.id,
        user_id=current_user.uid,
        user_email=current_user.email,
        user_name=current_user.name,
        role="member"
    )
    db.add(member)
    db.commit()

    return {"id": team.id, "name": team.name, "role": "member"}

@router.get("/mine")
def my_teams(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.uid).all()
    result = []
    for m in memberships:
        team = db.query(Team).filter(Team.id == m.team_id).first()
        if team:
            count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
            result.append({
                "id": team.id,
                "name": team.name,
                "join_code": team.join_code,
                "role": m.role,
                "member_count": count
            })
    return result

@router.get("/{team_id}/members")
def team_members(team_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.uid).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a team member")

    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return [{"user_id": m.user_id, "email": m.user_email, "name": m.user_name, "role": m.role} for m in members]

@router.post("/{team_id}/leave")
def leave_team(team_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.uid).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this team")

    db.delete(membership)

    remaining = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    if not remaining:
        team = db.query(Team).filter(Team.id == team_id).first()
        if team:
            db.delete(team)
    elif membership.role == "owner":
        next_member = remaining[0]
        next_member.role = "owner"

    db.commit()
    return {"status": "left"}
