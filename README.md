🇮🇹 Italiano · [🇬🇧 English](README.en.md)

# MultiGmail — plugin per Claude Code

Leggi la tua **Gmail da più account** direttamente in Claude Code. Quando chiedi
di leggere la posta, Claude ti chiede **su quale account** operare e gestisce il
login OAuth e la lettura delle email. **Sola lettura**: non invia, non cancella,
non modifica nulla.

Il plugin racchiude:
- un **MCP server** con 4 tool (`list_accounts`, `add_account`, `search_emails`, `read_email`);
- una **skill** che fa scattare il workflow "chiedi quale account" quando parli di Gmail/posta;
- auto-bootstrap delle dipendenze Python al primo avvio.

---

## Installazione (per gli utenti)

### 1. Aggiungi il marketplace e installa il plugin

```
/plugin marketplace add topastro73-it/multigmail
/plugin install multigmail
```

(In locale, per provarlo da una copia clonata: `/plugin marketplace add /percorso/della/cartella`.)

Le dipendenze Python vengono installate da sole al primo avvio (serve `python3`).

### 2. Crea le credenziali OAuth di Google (una tantum)

La Gmail API richiede un client OAuth **tuo**. Non può essere incluso nel plugin.

1. Vai su https://console.cloud.google.com/ e crea/seleziona un progetto.
2. **API e servizi → Libreria** → **Gmail API** → **Abilita**.
3. **Schermata consenso OAuth**: tipo **Esterno**, compila i campi obbligatori,
   e in **Utenti di test** aggiungi gli indirizzi Gmail che vorrai leggere.
4. **Credenziali → Crea credenziali → ID client OAuth** → tipo **App desktop** →
   **scarica il JSON**.
5. Salvalo come `~/.multigmail/credentials.json`:

   ```bash
   mkdir -p ~/.multigmail
   mv ~/Downloads/client_secret_*.json ~/.multigmail/credentials.json
   ```

### 3. Usa

Apri Claude Code e scrivi, ad esempio: «**leggimi le ultime mail**».
- Se non hai ancora account collegati, Claude esegue `add_account` (login Google nel browser).
- Poi ti elenca gli account e ti chiede quale usare, infine mostra le email.

Per aggiungere altri account: «collega un nuovo account Gmail».

#### Query utili (sintassi Gmail)
`is:unread` · `from:tizio@x.com` · `newer_than:7d` · `has:attachment`

---

## Struttura del progetto

```
multigmail/
├── .claude-plugin/
│   ├── plugin.json          # manifest del plugin (+ dichiarazione MCP server)
│   └── marketplace.json     # listing del marketplace
├── bin/run.sh               # launcher MCP (auto-bootstrap del venv)
├── scripts/
│   ├── ensure_deps.sh       # crea venv + installa dipendenze (idempotente)
│   └── install.sh           # setup manuale opzionale
├── hooks/hooks.json         # SessionStart: pre-installa le dipendenze
├── skills/gmail/SKILL.md    # workflow "chiedi quale account"
├── src/                     # codice MCP server (Python)
│   ├── server.py · gmail_auth.py · gmail_client.py · requirements.txt
└── tests/                   # test (parsing + gestione account)
```

---

## Pubblicare il plugin (per te, il manutentore)

1. Lo username GitHub `topastro73-it` è già impostato in
   `.claude-plugin/plugin.json` e nei README. Cambialo se fai un fork.
2. Fai push del contenuto di questa cartella sul tuo repo GitHub.
3. Gli altri lo installano con i comandi della sezione *Installazione*.

Sviluppo / test:

```bash
bash scripts/install.sh        # crea .venv e installa le dipendenze
.venv/bin/python -m pytest     # esegue i test
```

---

## Sicurezza

- Scope OAuth minimo: `gmail.readonly` (sola lettura).
- `credentials.json` e i token stanno in `~/.multigmail/`, **mai** nel repo.
- Revoca: cancella `~/.multigmail/tokens/<email>.json` e/o revoca l'app da
  https://myaccount.google.com/permissions.
