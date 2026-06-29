---
name: gmail
description: Leggere email Gmail da più account. Usa quando l'utente chiede di leggere/controllare/cercare la sua Gmail, posta, email o messaggi, senza specificare quale account.
---

# Lettura Gmail multi-account

Quando l'utente chiede di leggere, controllare o cercare la propria Gmail/posta/email, segui SEMPRE questo flusso usando i tool MCP `multigmail`:

1. **Identifica l'account.**
   - Se l'utente ha già detto chiaramente quale account usare, salta al punto 3.
   - Altrimenti chiama il tool `list_accounts`.

2. **Chiedi quale account** (se non già scelto).
   - Se ci sono account collegati, mostrali numerati e chiedi all'utente quale usare. NON sceglierne uno tu.
   - Se non ce n'è nessuno, spiega che va collegato un account e proponi di eseguire `add_account` (si aprirà il login Google nel browser). Se manca il file credenziali OAuth, indirizza l'utente al README per il setup una-tantum.

3. **Leggi/cerca.**
   - Usa `search_emails(account, query, max_results)` con la sintassi di ricerca Gmail (es. `is:unread`, `from:...`, `newer_than:7d`).
   - Per il contenuto completo di un messaggio usa `read_email(account, message_id)` con l'ID restituito dalla ricerca.

4. **Presenta i risultati** in modo conciso (mittente, oggetto, data, anteprima) e offri di aprire un messaggio specifico.

Sola lettura: questi tool non inviano, non cancellano e non modificano nulla.
