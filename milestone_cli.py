# RFC_V5_1_INIT
"""CLI for checking seasonal quest milestones."""

import argparse
from sqlalchemy.orm import Session
from db_models import SessionLocal, SystemState
from system_state_utils import log_event

KEY_SEASONAL = "seasonal_active"
KEY_QUEST = "quest_active"


def check_milestone() -> None:
    """Read seasonal and quest toggles."""
    db: Session = SessionLocal()
    try:
        seasonal = db.query(SystemState).filter(SystemState.key == KEY_SEASONAL).first()
        quest = db.query(SystemState).filter(SystemState.key == KEY_QUEST).first()
        print({
            "seasonal_active": bool(seasonal and seasonal.value == "1"),
            "quest_active": bool(quest and quest.value == "1"),
        })
        log_event(db, "rfc_init", {"action": "milestone_checked"})
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Milestone checker")
    parser.add_argument("--toggle-season", choices=["0", "1"], help="Set seasonal flag")
    parser.add_argument("--toggle-quest", choices=["0", "1"], help="Set quest flag")
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        if args.toggle_season is not None:
            state = db.query(SystemState).filter(SystemState.key == KEY_SEASONAL).first()
            if state:
                state.value = args.toggle_season
            else:
                db.add(SystemState(key=KEY_SEASONAL, value=args.toggle_season))
            log_event(db, "rfc_init", {"action": "toggle_season", "value": args.toggle_season})
            db.commit()
        if args.toggle_quest is not None:
            state = db.query(SystemState).filter(SystemState.key == KEY_QUEST).first()
            if state:
                state.value = args.toggle_quest
            else:
                db.add(SystemState(key=KEY_QUEST, value=args.toggle_quest))
            log_event(db, "rfc_init", {"action": "toggle_quest", "value": args.toggle_quest})
            db.commit()
    finally:
        db.close()

    check_milestone()


if __name__ == "__main__":
    main()
