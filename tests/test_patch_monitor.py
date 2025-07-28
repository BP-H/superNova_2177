import textwrap

from governance.patch_monitor import (check_file_compliance,
                                      check_patch_compliance)


def test_check_file_compliance(tmp_path):
    f = tmp_path / "module.py"
    f.write_text(
        (
            "# STRICTLY A SOCIAL MEDIA PLATFORM\n"
            "# Intellectual Property & Artistic Inspiration\n"
            "# Legal & Ethical Safeguards\n"
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
        "+ # STRICTLY A SOCIAL MEDIA PLATFORM\n"
        "+ # Intellectual Property & Artistic Inspiration\n"
        "+ # Legal & Ethical Safeguards\n"
        "+ pass\n"""
    )
    assert check_patch_compliance(patch) == []  # nosec B101


def test_check_patch_compliance_missing():
    patch = "@@\n+print('hi')\n"
    issues = check_patch_compliance(patch)
    assert issues and "missing required disclaimers" in issues[0].lower()  # nosec B101
