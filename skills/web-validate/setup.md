# web-validate setup

Read when `~/.config/web-validate/sites.json` does not exist, or when something breaks.

## First time

Tell the user this is a one-time setup.

1. **agent-browser.** `agent-browser --version`. Missing → ask, then `brew install agent-browser`
   (elsewhere `npm install -g agent-browser`) and `agent-browser install`.
2. **Sites.** For each site they check: URL; needs a login? If yes: login page, the sign-in
   button's label, and whether it shares a login with another site (then it shares the profile).
3. **Logins.** Sign each profile in (below). Once per profile, not per site.
4. **Write `sites.json` last** (a setup cut short leaves no file, so the next run starts over):

```json
{
  "profiles": { "work-sso": "~/.agent-browser/work-sso" },
  "sites": {
    "app-dev": { "url": "https://app-dev.example.com", "loginPath": "/login", "signIn": "Sign in", "profile": "work-sso" },
    "public-site": { "url": "https://www.example.com" }
  }
}
```

No `profile` = no login. Empty `signIn` = the site redirects to its login by itself. The file
names internal hosts: it stays on the user's machine, never in a repo.

## Sign a profile in

The user does this, on the **original** folder, in a visible browser:

```bash
agent-browser --session wv-login --profile <profile folder> --headed open "<url><loginPath>"
```

"A browser is open. Click <signIn>, finish the login (password, passkey, MFA), tell me when you
see the app." Wait, then `agent-browser --session wv-login close`. Never ask for the password.

It must be the user's own account: everything done on the site is recorded under that name.

## When something breaks

| Symptom | Fix |
| --- | --- |
| `agent-browser: command not found` | Step 1. |
| Site not in `sites.json` | Step 2 for that site, sign in if its profile is new, add the entry. |
| On the identity provider, a passkey/MFA page, or back on the login page after "Sign in" | Session expired: close, delete the copy, sign the profile in again, reopen. |
| Login page or button moved | Ask the user, update the entry. |
