import ast
from pathlib import Path


def test_async_client_calls():
    """All client calls that require awaiting are awaited."""
    source = Path("transcendental_resonance_frontend/src/quantum_futures.py").read_text()
    module = ast.parse(source)
    parents = {}

    class Visitor(ast.NodeVisitor):
        def generic_visit(self, node):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
                self.visit(child)

    Visitor().visit(module)

    def has_await(node):
        while node is not None:
            if isinstance(node, ast.Await):
                return True
            node = parents.get(node)
        return False

    target_funcs = {
        "get_speculative_futures",
        "generate_video_preview",
        "analyze_timeline",
    }
    missing = []
    for call in [n for n in ast.walk(module) if isinstance(n, ast.Call)]:
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr in target_funcs:
            if not has_await(call):
                missing.append(f"{func.attr} at line {call.lineno}")

    assert not missing, f"Calls missing await: {missing}"
