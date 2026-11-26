---
name: mobile-cert-pinning
description: >-
  Use when a native iOS (SwiftUI/URLSession) or Android (OkHttp/Ktor) app talks to its own backend
  and is being built, released or audited: adding or reviewing certificate (SSL) pinning, stopping
  people from reading the API with Proxyman, Charles or mitmproxy, preparing a TestFlight or Play
  release, checking whether an app already pins, or when a pinned app suddenly cannot connect
  (NSURLErrorDomain -1200/-1202, "Pin verification failed", SSLHandshakeException, Proxyman
  "999 Error"). Also for NSPinnedDomains, network_security_config.xml, pin-set, debug-overrides,
  抓包, 憑證綁定, SSL pinning, 中間人.
---

# mobile-cert-pinning

Every app that calls a backend we own pins that backend on both platforms before it ships.
Talk to the user in their language.

What pinning buys: a phone with a trusted Proxyman/mitmproxy profile can no longer read or change
our API traffic. What it does not: a jailbroken/rooted phone with Frida still can, so the backend
keeps its own auth, rate limits and validation, and the app holds no secrets.

## The shape of a correct setup

| Decision | Rule |
|---|---|
| Which hosts | Only hosts we run (API, our upload/download endpoints). Never third parties (Clerk, Firebase, Sentry, ad SDKs, image CDNs we don't run): they rotate on their own schedule. |
| What to pin | SPKI SHA-256 of the **root CA keys of every CA the host's TLS provider may issue from**. Never the leaf, never an intermediate (both rotate every few months). |
| How many | All of the provider's roots (at least two independent CAs). The roots in the served chain are not enough: providers switch CA without notice. |
| iOS | `NSAppTransportSecurity > NSPinnedDomains > <host> > NSPinnedCAIdentities` in Info.plist (iOS 14+). No code. `NSIncludesSubdomains: false`. |
| Android | `res/xml/network_security_config.xml` `<domain-config>` + `<pin-set expiration=…>`, referenced from `<application android:networkSecurityConfig>`. OkHttp/Ktor with the default trust manager obey it. No `CertificatePinner` on top (two lists drift). |
| Android expiration | 18–24 months out; the checker fails under 365 days left. It is the only way an old install recovers if every pinned CA disappears. iOS has no equivalent. |
| Debug builds | Android: `debug-overrides` with **only** `<certificates src="user" overridePins="true"/>`. iOS: same pins as release; a local dev server on another host (localhost, LAN IP) is unaffected. |
| One list | iOS and Android carry the identical host and pin list. `check_pins.py` enforces it. |
| Guard | A daily CI job runs `check_pins.py` against the live chain; a failure means the provider moved to a CA outside the list. |

### Cloudflare (Workers, Pages, proxied DNS with Universal SSL)

Cloudflare issues from Google Trust Services, Let's Encrypt and SSL.com and may switch at renewal.
Pin all eleven (GlobalSign Root CA because Google's chain is cross-signed by it):

```
hxqRlPTu1bMS/0DITB1SSu0vd4u/8l8TjPgfaAp63Gc=  GTS Root R1
Vfd95BwDeSQo+NUYxVEEIlvkOlWY2SalKK1lPhzOx78=  GTS Root R2
QXnt2YHvdHR3tJYmQIr0Paosp6t/nggsEGD4QJZ3Q0g=  GTS Root R3
mEflZT5enoR1FuXLgYYGqnVEoZvmf9c2bVBpiOjYQ0c=  GTS Root R4
K87oWBWM9UZfyddvDfoxL+8lpNyoUB2ptGtn0fv6G2Q=  GlobalSign Root CA
C5+lpZ7tcVwmwQIMcRtPbsQtWLABXhQzejna0wHFr8M=  ISRG Root X1 (Let's Encrypt)
diGVwiVYbubAI3RW4hB9xU8e/CH2GnkuvVFZE8zmgzI=  ISRG Root X2
K89VOmb1cJAN3TK6bf4ezAbJGC1mLcG2Dh97dnwr3VQ=  SSL.com TLS RSA Root CA 2022
G/ANXI8TwJTdF+AFBM8IiIUPEv0Gf6H5LA/b9guG4yE=  SSL.com TLS ECC Root CA 2022
0cRTd+vc1hjNFlHcLgLCHXUeWqn80bNDH/bs9qMTSPo=  SSL.com Root Certification Authority RSA
oyD01TTXvpfBro3QSZc1vIlcMjrdLTiL/M9mLCPX+Zo=  SSL.com Root Certification Authority ECC
```

Other providers: find which CAs they issue from (their docs), take each root from the OS root store
and hash it — on macOS:

```sh
security find-certificate -a -c "ISRG Root X1" -p /System/Library/Keychains/SystemRootCertificates.keychain \
  | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64
```

Then confirm the live chain ends in one of them: `check_pins.py` prints the chain and marks the match.

## Config

iOS, xcodegen `project.yml` (`targets.<app>.info.properties`; for a plain Info.plist write the same keys):

```yaml
NSAppTransportSecurity:
  NSPinnedDomains:
    api.example.com:
      NSIncludesSubdomains: false
      NSPinnedCAIdentities:
        - SPKI-SHA256-BASE64: hxqRlPTu1bMS/0DITB1SSu0vd4u/8l8TjPgfaAp63Gc=  # GTS Root R1
        # …one line per pin
```

Android, `app/src/main/res/xml/network_security_config.xml`:

```xml
<network-security-config>
  <domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="false">api.example.com</domain>
    <pin-set expiration="2028-06-30">
      <pin digest="SHA-256">hxqRlPTu1bMS/0DITB1SSu0vd4u/8l8TjPgfaAp63Gc=</pin> <!-- GTS Root R1 -->
      <!-- …one line per pin -->
    </pin-set>
  </domain-config>
  <!-- Debug builds also trust user-installed CAs, so we can still inspect our own traffic.
       Never add <certificates src="system"/> here: it makes debug builds skip the pins for real
       certificates too (a wrong pin still connects), so the wrong-pin test below proves nothing. -->
  <debug-overrides>
    <trust-anchors>
      <certificates src="user" overridePins="true" />
    </trust-anchors>
  </debug-overrides>
</network-security-config>
```

Put a comment next to both lists naming the other file and `check_pins.py`, so whoever edits one
edits both.

## Check script and CI

Copy `check_pins.py` (next to this file) into the app repo, e.g. `scripts/check_pins.py`:

```sh
python3 scripts/check_pins.py --ios ios/project.yml \
  --android android/app/src/main/res/xml/network_security_config.xml
```

It fails when the two lists differ, a host has fewer than two pins, the Android pin-set has no
expiration or under `--min-days` (365) left, `debug-overrides` disables pinning for real chains,
or no key in a host's live chain is pinned. `--offline` skips the network part.

Daily workflow (GitHub Actions; any runner with python3 and openssl):

```yaml
name: Cert pins
on:
  schedule: [{ cron: "17 2 * * *" }]
  workflow_dispatch:
  pull_request:
    paths: [ "ios/project.yml", "android/app/src/main/res/xml/network_security_config.xml", "scripts/check_pins.py", ".github/workflows/cert-pins.yml" ]
permissions: { contents: read }
jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/check_pins.py --ios ios/project.yml --android android/app/src/main/res/xml/network_security_config.xml
```

When it fails: add the new CA's root to both lists, ship both apps, keep the old pins.

## Prove it before shipping

Both directions on both platforms, from a clean install each time:

1. **Real pins connect.** Simulator/emulator: data loads.
2. **Wrong pin is refused.** Temporarily replace the whole list with one fake key
   (`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=`), build, launch: iOS logs a TLS error
   (`-1200`, "TLS錯誤導致安全連線失敗" / "An SSL error has occurred") and shows the app's
   offline/error state; Android never gets data. Restore the real list and rebuild. If the wrong
   pin still loads data, pinning is not active — on Android look first at `debug-overrides`.
3. **On a real phone with the release build** (TestFlight / Play test track) and Proxyman or
   mitmproxy with its CA trusted: our host's requests fail (Proxyman shows `CONNECT … 999 Error`
   within a few ms, mitmproxy logs "client does not trust the proxy's certificate"). Third-party
   hosts still decrypt; that is expected. Turn the proxy off: the app works again.

Report all three with what you saw (screenshots or log lines), not "should work".

## Auditing an app that may already ship

For each app repo: list the hosts its code calls (base URLs in both platforms), find
`NSPinnedDomains` and `networkSecurityConfig`, run `check_pins.py` if present. Report per app:
hosts we own, pinned on iOS (yes/no/wrong), pinned on Android, debug-overrides OK, daily check
present. "Android ignores user CAs since targetSdk 24" is not pinning: rooted phones with a system
CA, and every iPhone, still read the traffic.

## Common mistakes

| Mistake | Effect |
|---|---|
| Pinning the leaf or the intermediate | App breaks at the next renewal (weeks). |
| Pinning only the CA in today's chain | App breaks the day the provider switches CA. |
| `<certificates src="system"/>` in `debug-overrides` | Debug builds ignore the pins; the wrong-pin test passes for the wrong reason. |
| No Android `expiration` | An old install can never recover if all pinned CAs go away. |
| Pinning Firebase/Clerk/Sentry/CDN hosts | Login, analytics or images break when they rotate. |
| Different lists on iOS and Android | One platform breaks alone; nobody notices until users report it. |
| Custom `sslSocketFactory`/`TrustManager` in OkHttp | Network security config no longer applies; pins silently ignored. |
| Changing the backend host (custom domain, new worker) without moving the pins | The new host is unpinned, or the app cannot connect. |
| Only testing that the app still connects | Proves nothing about pinning; always run the wrong-pin test. |
