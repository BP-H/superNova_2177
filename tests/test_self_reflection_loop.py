# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import json
import uuid
import superNova_2177 as sn


def create_memory_agent(monkeypatch):
    monkeypatch.setattr(sn, "USE_IN_MEMORY_STORAGE", True)
    return sn.RemixAgent(
        cosmic_nexus=sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    )


def test_self_improve_loop(monkeypatch, tmp_path):
    agent = create_memory_agent(monkeypatch)

    add = sn.AddUserPayload(
        event="ADD_USER",
        user="tester",
        is_genesis=True,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=True,
        nonce=uuid.uuid4().hex,
    )
    agent.process_event(add)

    user = agent.storage.get_user("tester")
    root_coin_id = user["root_coin_id"]
    agent.storage.set_coin(
        root_coin_id,
        {"owner": "tester", "value": str(agent.config.ROOT_INITIAL_VALUE)},
    )

    mint = sn.MintPayload(
        event="MINT",
        user="tester",
        coin_id=uuid.uuid4().hex,
        value="50",
        root_coin_id=root_coin_id,
        references=[],
        improvement="",
        fractional_pct="0.0001",
        ancestors=[],
        timestamp=sn.ts(),
        is_remix=False,
        content="data",
        genesis_creator=None,
        karma_spent="0",
        nonce=uuid.uuid4().hex,
    )
    agent.process_event(mint)

    diary_path = tmp_path / "virtual_diary.json"
    with open(diary_path, "w") as f:
        json.dump([add, mint], f, default=str)

    before_entropy = float(sn.Config.ENTROPY_MULTIPLIER)
    revisions = agent.self_improve()
    after_entropy = float(sn.Config.ENTROPY_MULTIPLIER)

    assert revisions
    assert after_entropy != before_entropy
