from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class TankManifest:
    """Description for a tank and its exposed routes."""

    routes: Dict[str, str]
    allowed_state_mutation: bool = False
    required_payload: List[str] = field(default_factory=list)


class TankRegistry:
    """Central registry of tank modules and their manifests."""

    def __init__(self) -> None:
        self._tanks: Dict[str, TankManifest] = {}

    def register(self, name: str, manifest: TankManifest) -> None:
        self._tanks[name] = manifest

    def manifest(self, name: str) -> TankManifest:
        return self._tanks[name]

    def list_routes(self) -> Dict[str, str]:
        flat: Dict[str, str] = {}
        for manifest in self._tanks.values():
            flat.update(manifest.routes)
        return flat
