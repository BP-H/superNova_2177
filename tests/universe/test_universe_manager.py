import uuid
from universe_manager import UniverseManager


def test_initialize_for_entity_reuses_existing():
    manager = UniverseManager()
    uid1 = manager.initialize_for_entity("e1", "human")
    assert uid1
    u = manager.get_universe(uid1)
    assert u is not None
    assert u.owner_id == "e1"

    uid2 = manager.initialize_for_entity("e1", "human")
    assert uid2 == uid1

    uid3 = manager.initialize_for_entity("e1", "ai")
    assert uid3 != uid1
    assert manager.get_universe(uid3).owner_type == "ai"
