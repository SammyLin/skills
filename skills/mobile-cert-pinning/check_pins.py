#!/usr/bin/env python3
"""Check an app's certificate pins: iOS and Android pin the same hosts and keys, the Android
pin-set does not expire soon, and every pinned host's live certificate chain still matches.

    python3 check_pins.py --ios ios/project.yml --android android/app/src/main/res/xml/network_security_config.xml
    python3 check_pins.py --ios ios/App/Info.plist            # one platform is fine too
    python3 check_pins.py ... --min-days 365 --offline        # --offline skips the live chain check

--ios takes an Info.plist or an xcodegen project.yml (NSAppTransportSecurity > NSPinnedDomains).
Exit 1 on any problem: an app shipped with that config would lose its backend once the
listed failure happens. Standard library + the system openssl only.
"""
import argparse
import base64
import datetime
import hashlib
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SPKI = r"[A-Za-z0-9+/]{43}="


def ios_pins(path: Path):
    """Return {host: set(pins)} from an Info.plist or an xcodegen project.yml."""
    if path.suffix == ".plist":
        with path.open("rb") as f:
            domains = plistlib.load(f).get("NSAppTransportSecurity", {}).get("NSPinnedDomains", {})
        return {h: {p["SPKI-SHA256-BASE64"] for p in d.get("NSPinnedCAIdentities", [])
                     + d.get("NSPinnedLeafIdentities", [])} for h, d in domains.items()}
    # project.yml: walk the NSPinnedDomains block by indentation (no YAML dependency).
    lines = path.read_text().splitlines()
    out, start = {}, None
    for i, line in enumerate(lines):
        if re.match(r"^\s*NSPinnedDomains:\s*$", line):
            start = i
            break
    if start is None:
        return out
    base = len(lines[start]) - len(lines[start].lstrip())
    host_indent, host = None, None
    for line in lines[start + 1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base:
            break
        m = re.match(r"^\s*([A-Za-z0-9.\-]+):\s*(#.*)?$", line)
        if m and (host_indent is None or indent == host_indent) and "." in m.group(1):
            host_indent, host = indent, m.group(1)
            out[host] = set()
            continue
        pin = re.search(r"SPKI-SHA256-BASE64:\s*[\"']?(" + SPKI + ")", line)
        if pin and host:
            out[host].add(pin.group(1))
    return out


def android_pins(path: Path):
    """Return ({host: set(pins)}, [expiration dates], problems) from a network security config."""
    root = ET.parse(path).getroot()
    out, exps, problems = {}, [], []
    for dc in root.iter("domain-config"):
        hosts = [d.text.strip() for d in dc.findall("domain")]
        for ps in dc.findall("pin-set"):
            pins = {p.text.strip() for p in ps.findall("pin")}
            if ps.get("expiration"):
                exps.append(ps.get("expiration"))
            for h in hosts:
                out.setdefault(h, set()).update(pins)
    for do in root.iter("debug-overrides"):
        for c in do.iter("certificates"):
            if c.get("src") == "system":
                problems.append('debug-overrides lists <certificates src="system"/>: debug builds then '
                                "skip the pins for real certificates too (a wrong pin still connects). "
                                'Keep only <certificates src="user" overridePins="true"/>.')
    for ta in root.iter("trust-anchors"):
        for c in ta.iter("certificates"):
            if c.get("overridePins") == "true" and c.get("src") != "user":
                problems.append(f'overridePins="true" on src="{c.get("src")}" turns pinning off for real chains.')
    return out, exps, problems


def spki_sha256(pem: str) -> str:
    pub = subprocess.run(["openssl", "x509", "-noout", "-pubkey"], input=pem.encode(),
                         capture_output=True, check=True).stdout
    der = subprocess.run(["openssl", "pkey", "-pubin", "-outform", "DER"], input=pub,
                         capture_output=True, check=True).stdout
    return base64.b64encode(hashlib.sha256(der).digest()).decode()


def live_chain(host: str):
    out = subprocess.run(["openssl", "s_client", "-connect", f"{host}:443", "-servername", host, "-showcerts"],
                         input=b"", capture_output=True, timeout=30).stdout.decode(errors="replace")
    chain = []
    for pem in re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", out, re.S):
        subj = subprocess.run(["openssl", "x509", "-noout", "-subject", "-issuer"], input=pem.encode(),
                              capture_output=True).stdout.decode().strip().replace("\n", " | ")
        chain.append((subj, spki_sha256(pem)))
    return chain


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ios", type=Path, help="Info.plist or xcodegen project.yml")
    ap.add_argument("--android", type=Path, help="res/xml/network_security_config.xml")
    ap.add_argument("--min-days", type=int, default=365, help="Android pin-set must stay valid this long (default 365)")
    ap.add_argument("--offline", action="store_true", help="skip the live certificate chain check")
    a = ap.parse_args()
    if not a.ios and not a.android:
        ap.error("give --ios and/or --android")

    ok, sets = True, {}

    def fail(msg):
        nonlocal ok
        ok = False
        print(f"✗ {msg}")

    if a.ios:
        sets["iOS"] = ios_pins(a.ios)
        if not sets["iOS"]:
            fail(f"{a.ios}: no NSPinnedDomains found")
    if a.android:
        pins, exps, problems = android_pins(a.android)
        sets["Android"] = pins
        if not pins:
            fail(f"{a.android}: no <pin-set> found")
        for p in problems:
            fail(p)
        if pins and not exps:
            fail("Android pin-set has no expiration: an old install can never fall back if every pinned CA goes away")
        for e in exps:
            left = (datetime.date.fromisoformat(e) - datetime.date.today()).days
            if left < a.min_days:
                fail(f"Android pin-set expires {e} ({left} days): move it out before releasing")
    for name, hosts in sets.items():
        for h, pins in hosts.items():
            print(f"{name}: {h}: {len(pins)} pins")
            if len(pins) < 2:
                fail(f"{name}: {h} has {len(pins)} pin(s); keep at least one backup")
            if "." not in h:
                fail(f"{name}: {h!r} does not look like a host")
    if len(sets) == 2 and sets["iOS"] != sets["Android"]:
        for h in sorted(set(sets["iOS"]) | set(sets["Android"])):
            i, d = sets["iOS"].get(h, set()), sets["Android"].get(h, set())
            if i != d:
                fail(f"{h}: iOS and Android differ (only iOS: {sorted(i - d)}; only Android: {sorted(d - i)})")

    if not a.offline:
        all_hosts = {h: p for hosts in sets.values() for h, p in hosts.items()}
        for h, pins in sorted(all_hosts.items()):
            chain = live_chain(h)
            if not chain:
                fail(f"{h}: could not fetch the certificate chain")
                continue
            for subj, key in chain:
                print(f"  {'✓' if key in pins else ' '} {subj}")
            # A cross-signed root sent by the server shares its key with the self-signed root in the
            # device store, so a match anywhere in the served chain is enough.
            if any(key in pins for _, key in chain):
                print(f"✓ {h}: live chain matches a pin")
            else:
                fail(f"{h}: no key in the live chain is pinned: installed apps will fail to connect")

    print("OK" if ok else "FAILED: do not ship this config")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
