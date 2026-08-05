import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import notion_lib as n


def test_optional_unset_returns_default(monkeypatch):
    monkeypatch.delenv("SOME_VAR", raising=False)
    assert n.env("SOME_VAR", required=False, default="fallback") == "fallback"


def test_optional_empty_string_returns_default(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "")
    assert n.env("SOME_VAR", required=False, default="fallback") == "fallback"


def test_optional_set_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "actual")
    assert n.env("SOME_VAR", required=False, default="fallback") == "actual"


def test_required_unset_raises(monkeypatch):
    monkeypatch.delenv("SOME_VAR", raising=False)
    with pytest.raises(SystemExit):
        n.env("SOME_VAR", required=True)


def test_required_empty_string_raises(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "")
    with pytest.raises(SystemExit):
        n.env("SOME_VAR", required=True)


def test_required_set_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "actual")
    assert n.env("SOME_VAR", required=True) == "actual"
