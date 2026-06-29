[🇮🇹 Italiano](README.md) · 🇬🇧 English

# MultiGmail — a Claude Code plugin

Read your **Gmail across multiple accounts** straight from Claude Code. When you
ask to read your mail, Claude asks **which account** to use and handles the OAuth
login and the reading for you. **Read-only**: it never sends, deletes, or changes
anything.

The plugin bundles:
- an **MCP server** with 4 tools (`list_accounts`, `add_account`, `search_emails`, `read_email`);
- a **skill** that triggers the "ask which account" workflow whenever you mention Gmail/mail;
- auto-bootstrap of the Python dependencies on first run.

---

## Installation (for users)

### 1. Add the marketplace and install the plugin

```
/plugin marketplace add topastro73-it/multigmail
/plugin install multigmail
```

(Locally, to try a cloned copy: `/plugin marketplace add /path/to/the/folder`.)

The Python dependencies install themselves on first run (you need `python3`).

### 2. Create your Google OAuth credentials (one-time)

The Gmail API requires an OAuth client of **your own**. It can't be shipped inside
the plugin.

1. Go to https://console.cloud.google.com/ and create/select a project.
2. **APIs & Services → Library** → **Gmail API** → **Enable**.
3. **OAuth consent screen**: type **External**, fill in the required fields, and
   under **Test users** add the Gmail addresses you'll want to read.
4. **Credentials → Create credentials → OAuth client ID** → type **Desktop app** →
   **download the JSON**.
5. Save it as `~/.multigmail/credentials.json`:

   ```bash
   mkdir -p ~/.multigmail
   mv ~/Downloads/client_secret_*.json ~/.multigmail/credentials.json
   ```

### 3. Use it

Open Claude Code and type, for example: «**read me my latest emails**».
- If you have no linked accounts yet, Claude runs `add_account` (Google login in the browser).
- Then it lists your accounts and asks which one to use, and finally shows the emails.

To add more accounts: «link a new Gmail account».

#### Useful queries (Gmail syntax)
`is:unread` · `from:someone@x.com` · `newer_than:7d` · `has:attachment`

---

## Project layout

```
multigmail/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest (+ MCP server declaration)
│   └── marketplace.json     # marketplace listing
├── bin/run.sh               # MCP launcher (auto-bootstraps the venv)
├── scripts/
│   ├── ensure_deps.sh       # create venv + install deps (idempotent)
│   └── install.sh           # optional manual setup
├── hooks/hooks.json         # SessionStart: pre-installs the dependencies
├── skills/gmail/SKILL.md    # "ask which account" workflow
├── src/                     # MCP server code (Python)
│   ├── server.py · gmail_auth.py · gmail_client.py · requirements.txt
└── tests/                   # tests (parsing + account handling)
```

---

## Publishing the plugin (for you, the maintainer)

1. The GitHub username `topastro73-it` is already filled in across
   `.claude-plugin/plugin.json` and the READMEs. Change it if you fork.
2. Push the contents of this folder to your GitHub repo.
3. Others install it with the commands in the *Installation* section.

Development / testing:

```bash
bash scripts/install.sh        # create .venv and install dependencies
.venv/bin/python -m pytest     # run the tests
```

---

## Security

- Minimal OAuth scope: `gmail.readonly` (read-only).
- `credentials.json` and the tokens live in `~/.multigmail/`, **never** in the repo.
- Revoke: delete `~/.multigmail/tokens/<email>.json` and/or revoke the app at
  https://myaccount.google.com/permissions.
