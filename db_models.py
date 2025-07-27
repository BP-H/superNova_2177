# --- MODULE: db_models.py ---
# Database setup from FastAPI files
import os  # Added for DATABASE_URL environment variable
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    Float,
    JSON,
)
from sqlalchemy.orm import sessionmaker, relationship, Session

try:  # DeclarativeBase may not exist in stubbed sqlalchemy
    from sqlalchemy.orm import DeclarativeBase
except Exception:  # pragma: no cover - fallback class for tests
    class DeclarativeBase:
        metadata = type("Meta", (), {"create_all": lambda *a, **k: None, "drop_all": lambda *a, **k: None})()
from typing import TYPE_CHECKING
import datetime # Ensure datetime is imported for default values

# NOTE: In a real project, DATABASE_URL and SessionLocal would typically be imported from a central config/db module.
# For this extraction, we'll keep it self-contained for clarity, assuming it would be integrated.
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/transcendental_resonance" # Original hardcoded line
DB_MODE = os.getenv("DB_MODE", "local")
UNIVERSE_ID = os.getenv("UNIVERSE_ID", str(uuid.uuid4()))

if DB_MODE == "central":
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL must be set in central mode")
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", f"sqlite:///universe_{UNIVERSE_ID}.db"
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass

# Association Tables from FastAPI files
harmonizer_follows = Table(
    "harmonizer_follows",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
)
vibenode_likes = Table(
    "vibenode_likes",
    Base.metadata,
    Column("harmonizer_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
    Column("vibenode_id", Integer, ForeignKey("vibenodes.id"), primary_key=True),
)
group_members = Table(
    "group_members",
    Base.metadata,
    Column("harmonizer_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)
event_attendees = Table(
    "event_attendees",
    Base.metadata,
    Column("harmonizer_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
)
vibenode_entanglements = Table(
    "vibenode_entanglements",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("vibenodes.id"), primary_key=True),
    Column("target_id", Integer, ForeignKey("vibenodes.id"), primary_key=True),
    Column("strength", Float, default=1.0),
)
proposal_votes = Table(
    "proposal_votes",
    Base.metadata,
    Column("harmonizer_id", Integer, ForeignKey("harmonizers.id"), primary_key=True),
    Column("proposal_id", Integer, ForeignKey("proposals.id"), primary_key=True),
    Column("vote", String, nullable=False),
)


# ORM Models from all files
class Harmonizer(Base):
    __tablename__ = "harmonizers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    bio = Column(Text, default="")
    profile_pic = Column(String, default="default.jpg")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    species = Column(String, default="human", nullable=False)
    harmony_score = Column(String, default="100.0")
    creative_spark = Column(String, default="1000000.0")
    is_genesis = Column(Boolean, default=False)
    consent_given = Column(Boolean, default=True)
    cultural_preferences = Column(JSON, default=list)
    engagement_streaks = Column(JSON, default=dict)
    network_centrality = Column(Float, default=0.0)
    karma_score = Column(Float, default=0.0)
    last_passive_aura_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    vibenodes = relationship(
        "VibeNode", back_populates="author", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="harmonizer", cascade="all, delete-orphan"
    )
    messages_sent = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    messages_received = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    groups = relationship("Group", secondary=group_members, back_populates="members")
    events = relationship("Event", secondary=event_attendees, back_populates="attendees")
    following = relationship(
        "Harmonizer",
        secondary=harmonizer_follows,
        primaryjoin=(harmonizer_follows.c.follower_id == id),
        secondaryjoin=(harmonizer_follows.c.followed_id == id),
        backref="followers",
    )
    node_companies = relationship("CreativeGuild", back_populates="owner")
    simulations = relationship(
        "SimulationLog", back_populates="harmonizer", cascade="all, delete-orphan"
    )


class VibeNode(Base):
    __tablename__ = "vibenodes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    author_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    parent_vibenode_id = Column(Integer, ForeignKey("vibenodes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    media_type = Column(String, default="text")
    media_url = Column(String, nullable=True)
    fractal_depth = Column(Integer, default=0)
    echo = Column(String, default="0.0")
    engagement_catalyst = Column(String, default="0.0")
    negentropy_score = Column(String, default="0.0")
    tags = Column(JSON, default=list)
    patron_saint_id = Column(Integer, ForeignKey("ai_personas.id"), nullable=True)
    author = relationship("Harmonizer", back_populates="vibenodes")
    sub_nodes = relationship(
        "VibeNode",
        backref="parent_vibenode",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True,
    )
    comments = relationship(
        "Comment", back_populates="vibenode", cascade="all, delete-orphan"
    )
    likes = relationship(
        "Harmonizer", secondary=vibenode_likes, backref="liked_vibenodes"
    )
    entangled_with = relationship(
        "VibeNode",
        secondary=vibenode_entanglements,
        primaryjoin=(vibenode_entanglements.c.source_id == id),
        secondaryjoin=(vibenode_entanglements.c.target_id == id),
        backref="entangled_from",
    )
    creative_guild = relationship(
        "CreativeGuild", back_populates="vibenode", uselist=False
    )
    patron_saint = relationship("AIPersona", back_populates="vibenodes")


class CreativeGuild(Base):
    __tablename__ = "creative_guilds"
    id = Column(Integer, primary_key=True, index=True)
    vibenode_id = Column(
        Integer, ForeignKey("vibenodes.id"), unique=True, nullable=False
    )
    owner_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    legal_name = Column(String, nullable=False)
    guild_type = Column(String, default="art_collective")
    registration_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    vibenode = relationship("VibeNode", back_populates="creative_guild")
    owner = relationship("Harmonizer", back_populates="node_companies")


class GuinnessClaim(Base):
    __tablename__ = "guinness_claims"
    id = Column(Integer, primary_key=True, index=True)
    claimant_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    claim_type = Column(String, nullable=False)
    evidence_details = Column(Text)
    status = Column(String, default="pending")
    submission_timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class AIPersona(Base):
    __tablename__ = "ai_personas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    base_personas = Column(JSON, default=list)
    is_emergent = Column(Boolean, default=False)
    vibenodes = relationship("VibeNode", back_populates="patron_saint")


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    members = relationship(
        "Harmonizer", secondary=group_members, back_populates="groups"
    )
    events = relationship("Event", back_populates="group", cascade="all, delete-orphan")
    proposals = relationship(
        "Proposal", back_populates="group", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    vibenode_id = Column(
        Integer, ForeignKey("vibenodes.id"), nullable=False, index=True
    )
    parent_comment_id = Column(
        Integer, ForeignKey("comments.id"), nullable=True, index=True
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author = relationship("Harmonizer", back_populates="comments")
    vibenode = relationship("VibeNode", back_populates="comments")
    replies = relationship(
        "Comment",
        backref="parent_comment",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True,
    )


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    synchronization_potential = Column(Float, default=0.0)
    organizer_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    group = relationship("Group", back_populates="events")
    attendees = relationship(
        "Harmonizer", secondary=event_attendees, back_populates="events"
    )


class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    author_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    status = Column(String, default="open", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    voting_deadline = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON, nullable=True)
    group = relationship("Group", back_populates="proposals")
    votes = relationship(
        "ProposalVote", back_populates="proposal", cascade="all, delete-orphan"
    )


class ProposalVote(Base):
    __tablename__ = "proposal_votes_records"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(
        Integer, ForeignKey("proposals.id"), nullable=False, index=True
    )
    harmonizer_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    vote = Column(String, nullable=False)
    proposal = relationship("Proposal", back_populates="votes")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    harmonizer_id = Column(
        Integer, ForeignKey("harmonizers.id"), nullable=False, index=True
    )
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    harmonizer = relationship("Harmonizer", back_populates="notifications")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(
        Integer, ForeignKey("harmonizers.id"), nullable=False, index=True
    )
    receiver_id = Column(
        Integer, ForeignKey("harmonizers.id"), nullable=False, index=True
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sender = relationship(
        "Harmonizer", foreign_keys=[sender_id], back_populates="messages_sent"
    )
    receiver = relationship(
        "Harmonizer", foreign_keys=[receiver_id], back_populates="messages_received"
    )


class SimulationLog(Base):
    __tablename__ = "simulation_logs"
    id = Column(Integer, primary_key=True, index=True)
    harmonizer_id = Column(Integer, ForeignKey("harmonizers.id"), nullable=False)
    sim_type = Column(String, nullable=False, index=True)
    parameters = Column(JSON)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    harmonizer = relationship("Harmonizer", back_populates="simulations")


class LogEntry(Base):
    __tablename__ = "log_chain"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(Text)
    previous_hash = Column(String, nullable=False)
    current_hash = Column(String, unique=True, nullable=False)

    def chain_of_remix(self, db: Session) -> list[str]:
        """Return lineage of remix hashes leading to this entry."""
        chain = []
        prev = self.previous_hash
        while prev:
            entry = db.query(LogEntry).filter_by(current_hash=prev).first()
            if not entry:
                break
            chain.append(entry.current_hash)
            prev = entry.previous_hash
        return chain


class SystemState(Base):
    __tablename__ = "system_state"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)


class ValidatorReputation(Base):
    """Stores reputation scores for validators."""

    __tablename__ = "validator_reputations"

    validator_id = Column(String, primary_key=True)
    reputation = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)


# Add this below the SystemState class but before Coin to maintain ordering:
class HypothesisRecord(Base):
    """
    Represents a scientific hypothesis tracked by the system.
    Includes metadata, audit history, and evaluation stats.
    """
    __tablename__ = "hypotheses"

    id = Column(String, primary_key=True)  # e.g., HYP_1721495734_a1b2c3d4
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    status = Column(String, default="open", index=True)  # open / validated / falsified / merged / inconclusive / etc.
    score = Column(Float, default=0.0)
    entropy_change = Column(Float, default=0.0) # From associated audit metadata
    confidence_interval = Column(String, default="") # From hypothesis_reasoner
    metadata_json = Column(JSON, default=lambda: {})

    validation_log_ids = Column(JSON, default=lambda: [])  # LogEntry.id references
    audit_sources = Column(JSON, default=lambda: [])       # causal_trigger.py, audit_bridge.py etc. refs (SystemState keys)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    tags = Column(JSON, default=lambda: []) #
    notes = Column(Text, default="") # Summary of events/updates

    # Full history of evaluations / edits
    history = Column(JSON, default=lambda: []) # Detailed timestamped history of score/status changes

    # Relationships (Optional, for future direct linking)
    # E.g., validation_logs = relationship("LogEntry", secondary=hypothesis_validation_logs_table)

    def __repr__(self):
        return f"<HypothesisRecord(id={self.id}, status={self.status}, score={self.score})>"


# FUSED: Integrated additional models from v01_grok15.py, including Coin and MarketplaceListing
class Coin(Base):
    __tablename__ = "coins"
    coin_id = Column(String, primary_key=True, index=True)
    creator = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    value = Column(String, default="0.0")
    is_root = Column(Boolean, default=False)
    universe_id = Column(String, default="main")
    is_remix = Column(Boolean, default=False)
    references = Column(JSON, default=list)
    improvement = Column(Text, default="")
    fractional_pct = Column(String, default="0.0")
    ancestors = Column(JSON, default=list)
    content = Column(Text, default="")
    reactor_escrow = Column(String, default="0.0")
    reactions = Column(JSON, default=list)


class UniverseFork(Base):
    __tablename__ = "universe_forks"
    id = Column(String, primary_key=True)
    creator_id = Column(ForeignKey("harmonizers.id"))
    karma_at_fork = Column(Float)
    config = Column(JSON)
    timestamp = Column(DateTime)
    status = Column(String)


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"
    listing_id = Column(String, primary_key=True)
    coin_id = Column(String, nullable=False)
    seller = Column(String, nullable=False)
    price = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)


def init_db() -> None:
    """Create all tables defined in this module."""
    Base.metadata.create_all(bind=engine)

