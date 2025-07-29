# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import ast
import pathlib
import sys

PATTERNS = ["execute", "text"]


def _check_call(node: ast.Call, filename: str, results: list) -> None:
    if isinstance(node.func, ast.Attribute):
        name = node.func.attr
        if name == "execute" and node.args:
            arg = node.args[0]
            if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                results.append((filename, node.lineno, "possible dynamic SQL"))


def scan_file(path: pathlib.Path) -> list:
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            _check_call(node, str(path), results)
    return results


def main(base: str) -> int:
    issues = []
    for py in pathlib.Path(base).rglob("*.py"):
        issues.extend(scan_file(py))
    for file, line, msg in issues:
        print(f"{file}:{line}: {msg}")
    if issues:
        print(f"Found {len(issues)} potential SQL injection risks.")
    else:
        print("No obvious SQL injection patterns detected.")
    return 0


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(base))
