import textwrap

from governance.patch_monitor import (
    check_file_compliance,
    check_patch_compliance,
)
from disclaimers import (
    STRICTLY_SOCIAL_MEDIA,
    INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION,
    LEGAL_ETHICAL_SAFEGUARDS,
)


def test_check_file_compliance(tmp_path):
    f = tmp_path / "module.py"
    f.write_text(
        (
            f"# {STRICTLY_SOCIAL_MEDIA}\n"
            f"# {INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION}\n"
            f"# {LEGAL_ETHICAL_SAFEGUARDS}\n"
            "print('hello')\n"
        )
    )
    assert check_file_compliance(str(f)) == []  # nosec B101


def test_check_file_compliance_missing(tmp_path):
    f = tmp_path / "module.py"
    f.write_text("print('hi')\n")
    issues = check_file_compliance(str(f))
    assert issues and "Missing required disclaimers" in issues[0]  # nosec B101


def test_check_patch_compliance():
    patch = textwrap.dedent(
        """@@\n"
        f"+ # {STRICTLY_SOCIAL_MEDIA}\n"
        f"+ # {INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION}\n"
        f"+ # {LEGAL_ETHICAL_SAFEGUARDS}\n"
        "+ pass\n"""
    )
    assert check_patch_compliance(patch) == []  # nosec B101


def test_check_patch_compliance_missing():
    patch = "@@\n+print('hi')\n"
    issues = check_patch_compliance(patch)
    assert issues and "missing required disclaimers" in issues[0].lower()  # nosec B101


def test_check_patch_compliance_existing_file(tmp_path, monkeypatch):
    f = tmp_path / "module.py"
    f.write_text(
        (
            f"# {STRICTLY_SOCIAL_MEDIA}\n"
            f"# {INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION}\n"
            f"# {LEGAL_ETHICAL_SAFEGUARDS}\n"
            "print('hello')\n"
        )
    )
    patch = textwrap.dedent(
        f"""diff --git a/{f.name} b/{f.name}
        --- a/{f.name}
        +++ b/{f.name}
        @@
        +print('world')
        """
    )
    monkeypatch.chdir(tmp_path)
    assert check_patch_compliance(patch) == []  # nosec B101
