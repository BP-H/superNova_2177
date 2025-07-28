"""FastAPI router providing a login endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from superNova_2177 import get_db, login_for_access_token, Harmonizer
from universe_manager import manager as universe_manager

router = APIRouter()


@router.post("/login")
def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate and create a universe for the user."""
    token = login_for_access_token(form_data=form_data, db=db)
    user = (
        db.query(Harmonizer).filter(Harmonizer.username == form_data.username).first()
    )
    universe_id = universe_manager.initialize_for_entity(user.username)
    return {**token, "universe_id": universe_id}


# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
