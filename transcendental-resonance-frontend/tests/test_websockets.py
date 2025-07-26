import ast
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
MAIN_FILE = SRC_DIR / 'main.py'

def _has_async_func(name: str) -> bool:
    tree = ast.parse(MAIN_FILE.read_text())
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return True
    return False

def test_notifications_ws_defined():
    assert _has_async_func('notifications_ws')


def test_messages_ws_defined():
    assert _has_async_func('messages_ws')
