import sys
from pathlib import Path
import types

SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Ensure the local ``utils`` package is used instead of the repository root one
# Provide a lightweight NiceGUI stub so page modules import without the real package
class _DummyUI(types.SimpleNamespace):
    def __getattr__(self, name):
        def _dummy(*_a, **_k):
            return self
        return _dummy
    def page(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

ng = types.ModuleType('nicegui')
ng.ui = _DummyUI()
ng.background_tasks = types.SimpleNamespace(create=lambda *a, **k: None)
ng.element = types.SimpleNamespace(Element=object)
sys.modules['nicegui'] = ng

# Ensure the local ``utils`` package is used instead of the repository root one
import importlib
for name in list(sys.modules):
    if name == 'utils' or name.startswith('utils.'):
        sys.modules.pop(name)
sys.modules['utils'] = importlib.import_module('utils')
