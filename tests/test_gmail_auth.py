"""Test della gestione token/account (isolati via MULTIGMAIL_HOME)."""

import importlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def auth(tmp_path, monkeypatch):
    monkeypatch.setenv("MULTIGMAIL_HOME", str(tmp_path))
    import gmail_auth

    importlib.reload(gmail_auth)
    return gmail_auth


def test_list_accounts_empty(auth):
    assert auth.list_accounts() == []


def test_list_accounts_reads_email_field(auth):
    auth.TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    (auth.TOKENS_DIR / "uno.json").write_text(json.dumps({"_email": "uno@x.com"}))
    (auth.TOKENS_DIR / "due.json").write_text(json.dumps({"_email": "due@x.com"}))
    assert auth.list_accounts() == ["due@x.com", "uno@x.com"]


def test_require_credentials_missing(auth):
    with pytest.raises(auth.AuthError):
        auth._require_credentials()


def test_get_credentials_unknown_account(auth):
    with pytest.raises(auth.AuthError):
        auth.get_credentials("ignoto@x.com")
