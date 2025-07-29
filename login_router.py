
"""
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from superNova_2177 import (
    Harmonizer,
    InvalidConsentError,
    Token,
    create_access_token,
    get_db,
    verify_password,
)
from universe_manager import UniverseManager

router = APIRouter()



@router.post("/token", response_model=Token, tags=["Harmonizers"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(Harmonizer).filter(Harmonizer.username == form_data.username).first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user.consent_given:
        raise InvalidConsentError("User has revoked consent.")
    streaks = user.engagement_streaks or {}
    try:
        last_login = datetime.datetime.fromisoformat(
            streaks.get("last_login", "1970-01-01T00:00:00")
        )
    except ValueError:
        last_login = datetime.datetime(1970, 1, 1)
    now = datetime.datetime.utcnow()
    if (now.date() - last_login.date()).days == 1:
        streaks["daily"] = streaks.get("daily", 0) + 1
    elif now.date() > last_login.date():
        streaks["daily"] = 1
    streaks["last_login"] = now.isoformat()
    user.engagement_streaks = streaks
    db.commit()

    universe_id = UniverseManager.initialize_for_entity(user.id, user.species)
    access_token = create_access_token(
        {"sub": user.username, "universe_id": universe_id}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "universe_id": universe_id,
    }
