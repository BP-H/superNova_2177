# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import ast
from pathlib import Path


def test_no_duplicate_config_attributes():
    source = Path("config.py").read_text()
    module = ast.parse(source)
    cfg_class = next(
        node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "Config"
    )
    seen = set()
    duplicates = set()
    for node in cfg_class.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    if target.id in seen:
                        duplicates.add(target.id)
                    seen.add(target.id)
    assert not duplicates, f"Duplicate attributes found: {sorted(duplicates)}"
