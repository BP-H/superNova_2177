from sqlalchemy import text
from db_models import engine


def migrate() -> None:
    """Add unique constraint on branch_votes(branch_id, voter_id)."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_branch_vote_branch_voter ON branch_votes (branch_id, voter_id)"
            )
        )


if __name__ == "__main__":
    migrate()
    print("Added unique constraint on branch_votes(branch_id, voter_id)")
