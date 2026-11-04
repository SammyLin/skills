# web-validate

English · [繁體中文](README.zh-TW.md)

Checks a deployed web page in a real browser ([agent-browser](https://github.com/vercel-labs/agent-browser))
and brings back screenshots as evidence: public pages, and pages behind a login a headless agent
cannot or should not do itself (SSO with passkeys or MFA, a password).

It never logs in. You sign in once, by hand, in a browser profile; the agent works on a copy of
that profile, so the identity provider's session lets "Sign in" through without a passkey prompt.

The first run is a one-time setup: it installs agent-browser if needed, asks which sites you
check (URL, whether they need a login), and opens a visible browser once per login for you to
sign in. It saves that to `~/.config/web-validate/sites.json` on your machine, never in a repo.
After that it goes straight to work, and only comes back to you when something actually breaks
(a new site, an expired login).

It validates read-only by default, looks at every screenshot before calling it evidence,
attaches them to the GitHub or Azure DevOps item, and deletes its copy of your profile.

Use it in Claude Code: `/web-validate`, or say "check it on dev".

Each person signs in with their own account. A profile folder is a login: don't share it.

MIT.
