# mobile-cert-pinning

English · [繁體中文](README.zh-TW.md)

Certificate pinning for native iOS and Android apps that call a backend you run, so a phone with a
Proxyman, Charles or mitmproxy profile can no longer read or change the API traffic.

It pins the root CA keys of every CA your TLS provider may issue from (the full Cloudflare list is
included), on iOS with `NSPinnedDomains` and on Android with a network security config, one shared
list for both. `check_pins.py` keeps the two lists identical, catches a `debug-overrides` block that
quietly switches pinning off, warns before the Android pin-set expires and checks each host's live
certificate chain still matches; a daily CI job runs it so a CA change shows up before users can't
connect. Before shipping it proves both directions: real pins connect, a deliberately wrong pin is
refused, and on a real phone the proxy sees only failed handshakes.

Also audits existing apps: which hosts are pinned on which platform, and what is missing.

In Claude Code use `/mobile-cert-pinning`, or say "add SSL pinning", "stop people sniffing our API",
or "check whether our apps pin".

MIT.
