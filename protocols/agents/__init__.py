# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Convenience imports for all protocol agents.

This package dynamically discovers agent classes defined in modules within the
``protocols.agents`` package. Each discovered class is imported into the module
namespace so that users can simply do ``from protocols.agents import FooAgent``.

Any file inside this directory that defines a class ending with ``"Agent"`` and
deriving from :class:`protocols.core.internal_protocol.InternalAgentProtocol`
will be automatically imported.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import List

from protocols.core.internal_protocol import InternalAgentProtocol

__all__: List[str] = []

for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if is_pkg or module_name.startswith("_"):
        continue
    module = importlib.import_module(f"{__name__}.{module_name}")
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (
            name.endswith("Agent")
            and issubclass(obj, InternalAgentProtocol)
            and obj is not InternalAgentProtocol
        ):
            globals()[name] = obj
            __all__.append(name)

__all__.sort()
