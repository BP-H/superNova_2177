from __future__ import annotations

from typing import Any, Dict, List
import datetime

from frontend_bridge import register_route_once
from db_models import SessionLocal, Proposal, ProposalVote
from hook_manager import HookManager

ui_hook_manager = HookManager()


async def create_proposal_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new proposal and emit an event."""
    title = payload.get("title")
    author_id = payload.get("author_id")
    if not title or not author_id:
        raise ValueError("title and author_id are required")
    description = payload.get("description", "")
    group_id = payload.get("group_id")
    voting_deadline = payload.get("voting_deadline")
    if isinstance(voting_deadline, str):
        try:
            voting_deadline = datetime.datetime.fromisoformat(voting_deadline)
        except ValueError:
            voting_deadline = None
    if not voting_deadline:
        voting_deadline = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    db = SessionLocal()
    try:
        proposal = Proposal(
            title=title,
            description=description,
            group_id=group_id,
            author_id=author_id,
            voting_deadline=voting_deadline,
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        result = {"proposal_id": proposal.id}
    finally:
        db.close()
    await ui_hook_manager.trigger("proposal_created", result)
    return result


async def list_proposals_ui(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return all proposals and emit an event."""
    db = SessionLocal()
    try:
        records: List[Proposal] = db.query(Proposal).all()
        proposals = []
        for p in records:
            d = p.__dict__.copy()
            d.pop("_sa_instance_state", None)
            proposals.append(d)
        result = {"proposals": proposals}
    finally:
        db.close()
    await ui_hook_manager.trigger("proposals_listed", result)
    return result


async def vote_proposal_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record a vote for a proposal and emit an event."""
    proposal_id = payload.get("proposal_id")
    harmonizer_id = payload.get("harmonizer_id")
    vote = payload.get("vote")
    if not proposal_id or not harmonizer_id or not vote:
        raise ValueError("proposal_id, harmonizer_id and vote required")
    db = SessionLocal()
    try:
        record = ProposalVote(
            proposal_id=proposal_id,
            harmonizer_id=harmonizer_id,
            vote=str(vote),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        result = {"vote_id": record.id}
    finally:
        db.close()
    await ui_hook_manager.trigger(
        "proposal_voted", {"proposal_id": proposal_id, "vote_id": result["vote_id"]}
    )
    return result


register_route_once(
    "create_proposal",
    create_proposal_ui,
    "Create a new proposal",
    "proposals",
)
register_route_once(
    "list_proposals",
    list_proposals_ui,
    "List existing proposals",
    "proposals",
)
register_route_once(
    "vote_proposal",
    vote_proposal_ui,
    "Vote on a proposal",
    "proposals",
)
