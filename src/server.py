"""MultiGmail — MCP server per leggere Gmail da più account (sola lettura).

Espone 4 tool a Claude Code:
  - list_accounts : elenca gli account collegati
  - add_account   : collega un nuovo account (login nel browser)
  - search_emails : cerca email in un account scelto
  - read_email    : legge il contenuto completo di un'email
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

import gmail_auth
import gmail_client

mcp = FastMCP("multigmail")


@mcp.tool()
def list_accounts() -> str:
    """Elenca gli account Gmail già collegati.

    Chiama SEMPRE questo tool per primo quando l'utente chiede di leggere la
    Gmail senza specificare quale account, così da poter chiedere quale usare.
    """
    accounts = gmail_auth.list_accounts()
    if not accounts:
        return (
            "Nessun account collegato. Usa il tool add_account per collegarne "
            "uno (si aprirà il login Google nel browser)."
        )
    lines = [f"{i + 1}. {email}" for i, email in enumerate(accounts)]
    return "Account collegati:\n" + "\n".join(lines)


@mcp.tool()
def add_account() -> str:
    """Collega un nuovo account Gmail.

    Apre il login Google nel browser predefinito e salva il token in locale.
    Richiede che il file credenziali OAuth sia già presente (vedi README).
    """
    try:
        email = gmail_auth.add_account()
    except gmail_auth.AuthError as exc:
        return f"Errore: {exc}"
    return f"Account collegato: {email}"


@mcp.tool()
def search_emails(account: str, query: str = "", max_results: int = 10) -> str:
    """Cerca email in un account.

    Args:
        account: indirizzo email dell'account da usare (vedi list_accounts).
        query: query in sintassi Gmail (es. 'is:unread', 'from:tizio@x.com',
            'sub, newer_than:7d'). Vuoto = email più recenti.
        max_results: numero massimo di risultati (default 10).
    """
    try:
        results = gmail_client.search(account, query, max_results)
    except gmail_auth.AuthError as exc:
        return f"Errore: {exc}"
    if not results:
        return f"Nessuna email trovata in {account} per la query: {query!r}"
    blocks = []
    for r in results:
        blocks.append(
            f"ID: {r['id']}\n"
            f"Da: {r['from']}\n"
            f"Oggetto: {r['subject']}\n"
            f"Data: {r['date']}\n"
            f"Anteprima: {r['snippet']}"
        )
    return f"{len(results)} email in {account}:\n\n" + "\n\n---\n\n".join(blocks)


@mcp.tool()
def read_email(account: str, message_id: str) -> str:
    """Legge il contenuto completo di un'email dato il suo ID.

    Args:
        account: indirizzo email dell'account.
        message_id: ID del messaggio (dal risultato di search_emails).
    """
    try:
        msg = gmail_client.get_message(account, message_id)
    except gmail_auth.AuthError as exc:
        return f"Errore: {exc}"
    return (
        f"Da: {msg['from']}\n"
        f"A: {msg['to']}\n"
        f"Oggetto: {msg['subject']}\n"
        f"Data: {msg['date']}\n\n"
        f"{msg['body']}"
    )


if __name__ == "__main__":
    mcp.run()
