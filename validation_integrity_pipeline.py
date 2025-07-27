import json
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from validation_certifier import analyze_validation_integrity
from db_models import LogEntry


def run_validation_integrity_pipeline(
    validations: Union[str, List[Dict[str, Any]]], db: Session | None = None
) -> Dict[str, Any]:
    """Analyze validations and optionally store results in the database."""

    if isinstance(validations, str):
        try:
            parsed = json.loads(validations)
        except json.JSONDecodeError as exc:
            print(f"Failed to parse validations JSON: {exc}")
            return {}
        validations = parsed.get("validations", []) if isinstance(parsed, dict) else parsed

    try:
        result = analyze_validation_integrity(validations)
    except Exception as exc:
        print(f"Validation integrity analysis failed: {exc}")
        return {}

    if db is not None:
        try:
            db.add(
                LogEntry(
                    event_type="validation_integrity_result",
                    payload=json.dumps(result),
                    previous_hash="",
                    current_hash="",
                )
            )
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            print(f"Database error while storing integrity result: {exc}")
    return result
