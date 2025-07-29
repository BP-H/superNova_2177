import ast
from typing import List


def find_unawaited_api_calls(source: str) -> List[int]:
    """Return line numbers containing unawaited ``api_call`` invocations."""
    tree = ast.parse(source)

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack = []
            self.unawaited: List[int] = []

        def visit(self, node: ast.AST) -> None:  # type: ignore[override]
            self.stack.append(node)
            super().visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
            func = node.func
            if isinstance(func, ast.Name) and func.id == "api_call":
                parent = self.stack[-2] if len(self.stack) >= 2 else None
                if not isinstance(parent, ast.Await):
                    self.unawaited.append(node.lineno)
            self.generic_visit(node)

    visitor = Visitor()
    visitor.visit(tree)
    return visitor.unawaited
