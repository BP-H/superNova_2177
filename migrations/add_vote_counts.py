"""Add vote_count and yes_count columns to universe_branches table."""
from sqlalchemy import inspect, text
from db_models import engine

def migrate():
    with engine.begin() as conn:
        inspector = inspect(conn)
        cols = {c['name'] for c in inspector.get_columns('universe_branches')}
        if 'vote_count' not in cols:
            conn.execute(text('ALTER TABLE universe_branches ADD COLUMN vote_count INTEGER DEFAULT 0'))
        if 'yes_count' not in cols:
            conn.execute(text('ALTER TABLE universe_branches ADD COLUMN yes_count INTEGER DEFAULT 0'))

if __name__ == '__main__':
    migrate()
    print('Migration complete')
