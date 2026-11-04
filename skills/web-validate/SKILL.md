---
name: web-validate
description: >-
  Validate a deployed web page in a real browser with agent-browser: public pages, and pages
  behind a login the agent cannot or should not do itself (SSO with passkeys or MFA, a password),
  by reusing a browser profile the user signed into by hand. A one-time setup on first use; after
  that it goes straight to work. Use whenever a change has to be checked, screenshotted or
  accepted on a web page ("web validate", "check it on dev", "screenshot dev", "dev 驗證",
  "上 dev 看", "拍 dev 截圖", acceptance after a deploy), and before ever saying a login is
  impossible.
---

# web-validate

Look at a real, deployed page the way a user would, and come back with evidence.

A public page needs nothing more than a browser. The hard part is a page behind a login. Company
SSO usually ends in a passkey or MFA prompt a headless agent cannot answer, and a password is not
something the agent should hold. So the agent never logs in: **the user signs in once, by hand, in
a browser profile; the agent works on a copy of that profile**, and the existing session lets
"Sign in" go straight through. The same holds for SSO and for a plain username and password. One
login, one profile: every site behind the same identity provider shares it.

Out of scope: how a project signs in on localhost (minted sessions, test users, dev bypasses).
That belongs in the project's own docs; follow them, and use this skill for the browser work.

Talk to the user in their language.

## The site list

Everything the skill knows about the user's sites lives on their machine, never in a repo (it
names internal hosts): `~/.config/web-validate/sites.json`

```json
{
  "profiles": {
    "work-sso": "~/.agent-browser/work-sso"
  },
  "sites": {
    "app-dev": {
      "url": "https://app-dev.example.com",
      "loginPath": "/login",
      "signIn": "Sign in",
      "profile": "work-sso"
    },
    "marketing-site": {
      "url": "https://www.example.com"
    }
  }
}
```

- `profiles`: name → profile folder. One per login (identity provider + account).
- `sites.<name>.profile`: which profile signs in. **Omit it for a site with no login.**
- `sites.<name>.loginPath` / `signIn`: the login page and the button that starts the login.
  Leave `signIn` empty for a site that redirects to the login by itself.

**The file existing means setup is done.** Read it and go to step 1. Do not re-check the install,
the list or the login up front: each is fixed only when it actually breaks (see **When something
breaks**).

## 0. First-time setup (only when the file does not exist)

Tell the user this is a one-time setup, then:

1. **agent-browser.** `agent-browser --version`. Missing → ask, then
   `brew install agent-browser` (macOS; elsewhere `npm install -g agent-browser`) and
   `agent-browser install` (the Chromium it drives).
2. **Sites.** Ask which sites they validate, and for each one: its URL; does it need a login
   (no → no `profile`); if yes, its login page, the sign-in button's label, and whether it shares
   a login with a site already given (then it shares that profile; otherwise a new one, a folder
   under `~/.agent-browser/`).
3. **Logins.** For each profile, **Sign a profile in** below. One sign-in per profile, not per site.
4. **Write `sites.json` last**, show it, and continue with the task. Written last on purpose: a
   setup interrupted halfway leaves no file, so the next run starts it again.

## Sign a profile in (the user does this part)

Open a **visible** browser on the original profile folder and hand over:

```bash
agent-browser --session wv-login --profile <profile folder> --headed open "<url><loginPath>"
```

Tell the user: "A browser window is open. Click <signIn>, finish your login (password, passkey,
MFA, whatever it asks), and tell me when you see the app." Wait for their answer. Never ask the
user to give you the password instead. Then:

```bash
agent-browser --session wv-login close
```

This is the only time anything touches the original profile. It is the user's own login: it must
be **their** account, never a copy of somebody else's folder, because everything the agent then
does on the site is recorded under that person's name.

## 1. Open the site

A site with no `profile`: `agent-browser --session wv-<task> open <url>` and go to step 2.

A site with a profile: work on a copy. Never open the original for validation: parallel agents
lock it, and a crashed run can corrupt it.

```bash
COPY=<scratch dir>/wv-<task>/profile
cp -R <profile folder> "$COPY"
agent-browser --session wv-<task> --profile "$COPY" open "<url><loginPath>"
agent-browser --session wv-<task> snapshot -i      # click the sign-in button by its ref
agent-browser --session wv-<task> get url          # must have left the login page
```

- Always pass `--session`: the default session is shared with every other agent on the machine.
- `--profile ignored: daemon already running` on the first `open` means an old daemon owns that
  session name: `close` it and open again. The same warning on later commands is normal.
- Signed in → note who (the user menu usually shows the name) and go on.

## When something breaks

Fix only the part that broke, then carry on with the task:

| Symptom | Fix |
| --- | --- |
| `agent-browser: command not found` | Setup step 1 (install). |
| The site is not in `sites.json` | Setup step 2 for that one site, sign its profile in if it is a new one, add the entry. |
| After "Sign in" you are on the identity provider, a passkey/MFA prompt, or back on the login page | The session expired: close, delete the copy, **Sign a profile in** again, then redo step 1. Never type credentials. |
| The login page or button moved | Ask the user, update that site's entry. |

## 2. Validate

- **Read-only by default.** Look and screenshot. Anything that writes (save, delete, send, invite)
  happens as the user: do it only when the task needs it, and say so first.
- Set a viewport before screenshots: `agent-browser --session wv-<task> set viewport 1440 900`.
- Refs go stale after any click: `snapshot -i` again before the next one. Content below the fold
  needs `scrollintoview @ref` first.
- Stay off native `confirm()` / `prompt()` dialogs: they hang agent-browser.
- **Look at every screenshot** before using it as evidence. A blank page, a spinner or a login
  page is a failed check, not a result.
- Check what the change was about, not just that the page loads: the thing that should be gone is
  gone, the thing that should appear appears, for the role it was meant for.

## 3. Report the evidence

Where the work is tracked, attach the screenshots there, and say in one line what each shows.

- **GitHub** (issue/PR): drag-and-drop is the only upload path; save the screenshots and give the
  user the paths, or describe them in a comment.
- **Azure DevOps work item**: upload, then put the image in a comment.

  ```bash
  TOK=$(az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv)
  URL=$(curl -s -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/octet-stream" \
    --data-binary @shot.png "https://dev.azure.com/<org>/<project>/_apis/wit/attachments?fileName=shot.png&api-version=7.1" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])")
  az boards work-item update --id <id> --org https://dev.azure.com/<org> \
    --discussion "What this shows.<br><img src=\"$URL\">"
  ```

- **Azure DevOps pull request**: the same upload to
  `…/_apis/git/repositories/<repo>/pullRequests/<id>/attachments/<name>.png`, then
  `![name](<url>)` in the description.

## 4. Clean up

```bash
agent-browser --session wv-<task> close
rm -rf <scratch dir>/wv-<task>/profile      # it carries the user's SSO cookies
```

If the delete is refused, give the user the exact path to remove. Never leave a copy in a shared
or synced folder.

## When there is no browser at all

Weaker evidence, labelled as such: fetch the site's HTML, follow its JavaScript bundles
recursively with `curl`, and search them for the strings the change added or removed. An
unauthenticated request to the site's API usually proves nothing (many hosts answer with the
single-page app's HTML or a proxy error before the API is reached).
