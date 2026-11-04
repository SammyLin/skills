# web-validate

English · [繁體中文](README.zh-TW.md)

Checks a deployed web page in a real browser ([agent-browser](https://github.com/vercel-labs/agent-browser))
and brings back screenshots as evidence: public pages, and pages behind a login a headless agent
cannot or should not do itself (SSO with passkeys or MFA, a password).

It never logs in. You sign in once, by hand, in a browser profile; the agent works on a copy of
that profile, so the identity provider's session lets "Sign in" through without a passkey prompt.

Every run starts with a setup gate, so a fresh machine walks you through it:

1. agent-browser installed (offers to install it and its browser)
2. the site listed in `~/.config/web-validate/sites.json` (asks you for the URL and login page;
   the list stays on your machine, never in a repo)
3. for a site that needs a login, the profile signed in (opens a visible browser for you to log
   in, then checks it worked); a site with no login skips this

Then it validates read-only by default, looks at every screenshot before calling it evidence,
attaches them to the GitHub or Azure DevOps item, and deletes its copy of your profile.

Use it in Claude Code: `/web-validate`, or say "check it on dev".

Each person signs in with their own account. A profile folder is a login: don't share it.

MIT.
