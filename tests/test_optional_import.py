import types
import sys
import pytest

from optional_import import optional_import


def test_optional_import_present(monkeypatch):
    fake = types.ModuleType("fakepkg")
    fake.foo = lambda: "bar"
    monkeypatch.setitem(sys.modules, "fakepkg", fake)
    func = optional_import("fakepkg", "foo")
    assert func() == "bar"


def test_optional_import_missing_attr():
    func = optional_import("fake_missing_mod", "foo")
    with pytest.raises(ImportError):
        func()


def test_optional_import_module_missing():
    mod = optional_import("another_missing_pkg")
    with pytest.raises(ImportError):
        mod.some_attr
