"""Test di parsing del client Gmail con risposte API mockate (niente rete)."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import gmail_client


def b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("utf-8")


def test_extract_body_prefers_plain_text():
    payload = {
        "mimeType": "multipart/alternative",
        "parts": [
            {"mimeType": "text/plain", "body": {"data": b64("ciao testo")}},
            {"mimeType": "text/html", "body": {"data": b64("<p>ciao html</p>")}},
        ],
    }
    assert gmail_client.extract_body(payload) == "ciao testo"


def test_extract_body_falls_back_to_html():
    payload = {
        "mimeType": "text/html",
        "body": {"data": b64("<p>solo html</p>")},
    }
    assert gmail_client.extract_body(payload) == "<p>solo html</p>"


def test_extract_body_nested_parts():
    payload = {
        "mimeType": "multipart/mixed",
        "parts": [
            {
                "mimeType": "multipart/alternative",
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": b64("annidato")}},
                ],
            }
        ],
    }
    assert gmail_client.extract_body(payload) == "annidato"


def test_header_lookup_case_insensitive():
    headers = [{"name": "From", "value": "a@b.com"}]
    assert gmail_client._header(headers, "from") == "a@b.com"
    assert gmail_client._header(headers, "Subject") == ""


@patch("gmail_client._get_service")
def test_search_builds_summary(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    service.users().messages().list().execute.return_value = {
        "messages": [{"id": "m1"}]
    }
    service.users().messages().get().execute.return_value = {
        "id": "m1",
        "snippet": "anteprima",
        "payload": {
            "headers": [
                {"name": "From", "value": "tizio@x.com"},
                {"name": "Subject", "value": "Oggetto"},
                {"name": "Date", "value": "Mon, 1 Jan 2026"},
            ]
        },
    }
    results = gmail_client.search("me@x.com", "is:unread", 5)
    assert results == [
        {
            "id": "m1",
            "from": "tizio@x.com",
            "subject": "Oggetto",
            "date": "Mon, 1 Jan 2026",
            "snippet": "anteprima",
        }
    ]


@patch("gmail_client._get_service")
def test_get_message_full(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    service.users().messages().get().execute.return_value = {
        "id": "m1",
        "payload": {
            "headers": [
                {"name": "From", "value": "a@b.com"},
                {"name": "To", "value": "me@x.com"},
                {"name": "Subject", "value": "Ciao"},
                {"name": "Date", "value": "Mon, 1 Jan 2026"},
            ],
            "mimeType": "text/plain",
            "body": {"data": b64("corpo del messaggio")},
        },
    }
    msg = gmail_client.get_message("me@x.com", "m1")
    assert msg["from"] == "a@b.com"
    assert msg["to"] == "me@x.com"
    assert msg["subject"] == "Ciao"
    assert msg["body"] == "corpo del messaggio"
