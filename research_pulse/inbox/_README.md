# inbox/

Drop raw chat exports here. Everything in this directory except this README
is **gitignored** — team chat is assumed private.

## Naming convention

```
YYYY-WXX_<source>.<ext>
```

Examples:
- `2026-W17_slack-dexterous.txt`
- `2026-W17_telegram-research.json`
- `2026-W17_slack-dexterous.zip`  (for multi-channel exports)

## Supported formats

The digest prompt (`/.claude/prompts/pulse-digest.md`) expects speakers and
timestamps but does not assume a specific format. Any of these work:

- Slack channel export (txt or JSON)
- Telegram chat export (HTML or JSON)
- Plain markdown / text with one message per line
- Chat copy-paste with speaker names visible

If timestamps or speaker names are missing, the digest confidence will cap at
`low`. That is the expected behavior — do not fabricate metadata.

## Do not

- Commit transcripts to the repo (gitignore handles this; do not override).
- Move transcripts out of `inbox/` after digestion. The hint file in
  `research_pulse/YYYY-WXX.md` is the committed artifact; the raw source
  stays here and can be deleted locally once the hint is reviewed.
- Paste more than one week's window into one file — one file per week keeps
  the digest prompt's window detection reliable.
