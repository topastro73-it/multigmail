"""OAuth e gestione token per account Gmail multipli.

Tutti i dati sensibili (client OAuth e token) vivono in ~/.multigmail/,
fuori dal repository. Scope minimo: sola lettura.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Sola lettura. getProfile (per ricavare l'indirizzo email) funziona con
# questo scope, quindi non servono scope aggiuntivi.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = Path(os.environ.get("MULTIGMAIL_HOME", Path.home() / ".multigmail"))
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKENS_DIR = BASE_DIR / "tokens"


class AuthError(Exception):
    """Errore di configurazione o autenticazione leggibile dall'utente."""


def _ensure_dirs() -> None:
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)


def _token_path(email: str) -> Path:
    # L'email è usata come nome file; sanifichiamo per sicurezza.
    safe = email.strip().lower().replace("/", "_").replace("\\", "_")
    return TOKENS_DIR / f"{safe}.json"


def _require_credentials() -> None:
    if not CREDENTIALS_FILE.exists():
        raise AuthError(
            f"File credenziali OAuth mancante: {CREDENTIALS_FILE}\n"
            "Crea un progetto Google Cloud, abilita la Gmail API, crea "
            "credenziali OAuth di tipo 'Desktop app' e salva il file "
            f"scaricato come {CREDENTIALS_FILE}. Vedi il README per i passi."
        )


def _email_for_credentials(creds: Credentials) -> str:
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    return profile["emailAddress"]


def list_accounts() -> list[str]:
    """Restituisce gli indirizzi email degli account già collegati."""
    if not TOKENS_DIR.exists():
        return []
    emails: list[str] = []
    for token_file in sorted(TOKENS_DIR.glob("*.json")):
        try:
            data = json.loads(token_file.read_text())
            emails.append(data.get("_email", token_file.stem))
        except (json.JSONDecodeError, OSError):
            continue
    return emails


def add_account() -> str:
    """Avvia il flusso OAuth nel browser e salva il token.

    Ritorna l'indirizzo email dell'account collegato.
    """
    _require_credentials()
    _ensure_dirs()

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    email = _email_for_credentials(creds)
    _save_credentials(email, creds)
    return email


def _save_credentials(email: str, creds: Credentials) -> None:
    _ensure_dirs()
    data = json.loads(creds.to_json())
    data["_email"] = email
    _token_path(email).write_text(json.dumps(data, indent=2))


def get_credentials(email: str) -> Credentials:
    """Carica il token di un account, aggiornandolo se scaduto."""
    path = _token_path(email)
    if not path.exists():
        accounts = list_accounts()
        raise AuthError(
            f"Account '{email}' non collegato. "
            f"Account disponibili: {accounts or 'nessuno'}. "
            "Usa add_account per collegarne uno."
        )
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save_credentials(email, creds)
        else:
            raise AuthError(
                f"Token per '{email}' non valido e non rinnovabile. "
                "Ricollega l'account con add_account."
            )
    return creds
