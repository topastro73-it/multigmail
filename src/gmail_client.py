"""Wrapper di sola lettura sulla Gmail API per un singolo account."""

from __future__ import annotations

import base64
from typing import Any

from googleapiclient.discovery import build

from gmail_auth import get_credentials


def _get_service(email: str):
    creds = get_credentials(email)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _header(headers: list[dict[str, str]], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _decode_part(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")


def extract_body(payload: dict[str, Any]) -> str:
    """Estrae il testo del messaggio, preferendo text/plain a text/html."""
    plain: str | None = None
    html: str | None = None

    def walk(part: dict[str, Any]) -> None:
        nonlocal plain, html
        mime = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")
        if data:
            if mime == "text/plain" and plain is None:
                plain = _decode_part(data)
            elif mime == "text/html" and html is None:
                html = _decode_part(data)
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    if plain is not None:
        return plain
    if html is not None:
        return html
    return ""


def search(email: str, query: str = "", max_results: int = 10) -> list[dict[str, str]]:
    """Cerca messaggi e restituisce un riepilogo (id, mittente, oggetto, data, snippet).

    `query` usa la sintassi di ricerca Gmail (es. 'is:unread', 'from:foo@bar.com').
    """
    service = _get_service(email)
    resp = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = resp.get("messages", [])
    results: list[dict[str, str]] = []
    for msg in messages:
        full = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = full.get("payload", {}).get("headers", [])
        results.append(
            {
                "id": full["id"],
                "from": _header(headers, "From"),
                "subject": _header(headers, "Subject"),
                "date": _header(headers, "Date"),
                "snippet": full.get("snippet", ""),
            }
        )
    return results


def get_message(email: str, message_id: str) -> dict[str, str]:
    """Restituisce il contenuto completo di un messaggio."""
    service = _get_service(email)
    full = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = full.get("payload", {})
    headers = payload.get("headers", [])
    return {
        "id": full["id"],
        "from": _header(headers, "From"),
        "to": _header(headers, "To"),
        "subject": _header(headers, "Subject"),
        "date": _header(headers, "Date"),
        "body": extract_body(payload),
    }
