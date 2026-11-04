---
name: web-validate
description: >-
  Validate a deployed web page in a real browser with agent-browser, including pages behind a
  login the agent cannot or should not do itself (SSO with passkeys or MFA, a password), by
  reusing a browser profile the user signed into by hand. One-time setup on first use. Use
  whenever a change has to be checked, screenshotted or accepted on a web page ("web validate",
  "check it on dev", "dev 驗證", "上 dev 看", "拍 dev 截圖"), and before ever saying a login is
  impossible.
---

# web-validate

The agent never logs in. The user signed in once, by hand, in a browser profile; you work on a
copy of it, so "Sign in" goes straight through.

`~/.config/web-validate/sites.json` holds the user's sites and profiles. **Missing → read
[setup.md](setup.md) first.** Present → go straight to work.

## Open the site

No `profile` on the site → `agent-browser --session wv-<task> open <url>`.

With a profile, always on a copy (the original gets locked or corrupted):

```bash
COPY=<scratch dir>/wv-<task>/profile
cp -R <profile folder> "$COPY"
agent-browser --session wv-<task> --profile "$COPY" open "<url><loginPath>"
# snapshot -i, click <signIn>, then get url: you must have left the login page
```

Always pass `--session`. "`--profile ignored: daemon already running`" on the first `open` →
`close` that session and open again.

Something broke (command missing, site not listed, back on a login or passkey page) → the fix is
in [setup.md](setup.md). Never type credentials.

## Validate

- Read-only by default. A write happens as the user: only when the task needs it, say so first.
- `set viewport 1440 900` before screenshots; `snapshot -i` again after every click.
- Look at every screenshot. A blank, spinner or login page is a failed check.
- Check the change itself (gone is gone, new is there, for the right role), not just that it loads.

Attach the screenshots where the work is tracked: [evidence.md](evidence.md).

## Clean up

`agent-browser --session wv-<task> close`, then delete the copy (it carries the user's SSO
cookies). If the delete is refused, give the user the exact path.
