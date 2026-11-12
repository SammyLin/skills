#!/usr/bin/env python3
"""Lint a Firebase / GA4 tracking-plan.yaml and check iOS / Android code against it.

    python3 plan_check.py tracking-plan.yaml [--src ios/ --src android/]
    python3 plan_check.py --selftest

YAML needs PyYAML (`uv run --with pyyaml python3 plan_check.py ...`); a .json plan needs nothing.
Exit 1 on any error. Warnings don't fail.

Code check (per --src dir, one per platform):
  missing  - plan event whose name (or SDK constant, e.g. AnalyticsEventSignUp /
             Event.SIGN_UP) never appears in that dir
  unknown  - snake_case literal in an analytics module file (name contains analytic/track/event)
             that is not a plan event, parameter, enum value, screen or user property
"""
import json
import re
import sys
from pathlib import Path

NAME = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
USER_PROP = re.compile(r"^[a-z][a-z0-9_]{0,23}$")
LITERAL = re.compile(r"\"([a-z][a-z0-9_]*)\"")
EVENTISH = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")
TYPES = {"string", "integer", "number", "boolean", "datetime"}
CATEGORIES = {"lifecycle", "core_value", "engagement", "monetization", "configuration", "navigation"}
PII = {"email", "phone", "phone_number", "name", "first_name", "last_name", "full_name", "address",
       "password", "token", "ip", "ip_address", "lat", "lng", "latitude", "longitude", "query",
       "search_query", "search_term", "message", "comment", "note", "birthday"}
# Firebase logs these itself and refuses them from logEvent.
RESERVED = {"app_clear_data", "app_exception", "app_remove", "app_store_refund",
            "app_store_subscription_cancel", "app_store_subscription_convert",
            "app_store_subscription_renew", "app_update", "app_upgrade", "dynamic_link_app_open",
            "dynamic_link_app_update", "dynamic_link_first_open", "error", "first_open",
            "first_visit", "in_app_purchase", "notification_dismiss", "notification_foreground",
            "notification_open", "notification_receive", "os_update", "session_start",
            "user_engagement"}
RESERVED_PREFIX = ("firebase_", "google_", "ga_")
# GA4 recommended events: exact names, exempt from the past-tense rule.
RECOMMENDED = {"ad_impression", "add_payment_info", "add_shipping_info", "add_to_cart",
               "add_to_wishlist", "begin_checkout", "campaign_details", "earn_virtual_currency",
               "generate_lead", "join_group", "level_end", "level_start", "level_up", "login",
               "post_score", "purchase", "refund", "remove_from_cart", "screen_view", "search",
               "select_content", "select_item", "select_promotion", "share", "sign_up",
               "spend_virtual_currency", "tutorial_begin", "tutorial_complete",
               "unlock_achievement", "view_cart", "view_item", "view_item_list", "view_promotion",
               "view_search_results"}
PAST_IRREGULAR = {"sent", "shown", "seen", "made", "done", "paid", "set", "won", "lost", "read", "begun"}
LIMITS = {"events": 500, "event_dimensions": 50, "event_metrics": 50, "user_properties": 25,
          "key_events": 30, "params_per_event": 25}
SRC_EXT = {".swift", ".kt", ".java", ".dart", ".ts", ".tsx", ".js"}
SKIP_DIRS = {"build", ".build", "Pods", "DerivedData", ".gradle", "node_modules", ".git"}


def sdk_constants(event):
    """AnalyticsEventSignUp (Swift/ObjC) and Event.SIGN_UP (Kotlin/Java) for a recommended event."""
    if event not in RECOMMENDED:
        return ()
    return ("AnalyticsEvent" + "".join(w.title() for w in event.split("_")), "Event." + event.upper())


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML missing: uv run --with pyyaml python3 plan_check.py ...  (or pip install pyyaml)")
    return yaml.safe_load(text)


def is_pii(name):
    return name in PII or "email" in name or "phone" in name


def check_plan(plan):
    err, warn = [], []
    meta = plan.get("meta") or {}
    for k in ("product", "version", "destinations", "pii_policy", "core_value_event"):
        if not meta.get(k):
            err.append(f"meta.{k} missing")
    auto = set(plan.get("auto_events") or [])
    builtin = set(plan.get("builtin_dimensions") or [])
    screens = list(plan.get("screens") or [])

    user_props = {}
    for up in plan.get("user_properties") or []:
        n = up.get("name", "")
        user_props[n] = up
        if not USER_PROP.match(n) or n.startswith(RESERVED_PREFIX):
            err.append(f"user property {n or '?'}: snake_case, <= 24 chars, no firebase_/google_/ga_ prefix")
        if is_pii(n):
            err.append(f"user property {n}: PII")
        if up.get("type") not in TYPES:
            err.append(f"user property {n}: type must be one of {sorted(TYPES)}")
        for v in up.get("enum") or []:
            if len(str(v)) > 36:
                err.append(f"user property {n}: value '{v}' > 36 chars")
    if len(user_props) > LIMITS["user_properties"]:
        err.append(f"{len(user_props)} user properties, Firebase max {LIMITS['user_properties']}")

    events, prop_types, all_props, enum_values = {}, {}, set(), set()
    registered = {"dimension": set(), "metric": set()}
    for ev in plan.get("events") or []:
        n = ev.get("name", "")
        where = f"event {n or '?'}"
        if n in events:
            err.append(f"{where}: duplicate")
        events[n] = ev
        if not NAME.match(n):
            err.append(f"{where}: name must be snake_case object_action, <= 40 chars, start with a letter")
        if n in RESERVED or n.startswith(RESERVED_PREFIX):
            err.append(f"{where}: reserved by Firebase (list it under auto_events instead)")
        # any word, so phrasal verbs pass: signed_up, opted_out
        if n not in RECOMMENDED and not any(w.endswith("ed") or w in PAST_IRREGULAR for w in n.split("_")):
            warn.append(f"{where}: not a GA4 recommended event and no past-tense verb (e.g. alert_created)")
        if ev.get("category") not in CATEGORIES:
            err.append(f"{where}: category must be one of {sorted(CATEGORIES)}")
        for k in ("description", "trigger"):
            if not ev.get(k):
                err.append(f"{where}: {k} missing")
        props = ev.get("properties") or []
        if len(props) > LIMITS["params_per_event"]:
            err.append(f"{where}: {len(props)} parameters, Firebase max {LIMITS['params_per_event']}")
        for p in props:
            pn, pt = p.get("name", ""), p.get("type")
            pw = f"{where}.{pn or '?'}"
            all_props.add(pn)
            if not NAME.match(pn) or pn.startswith(RESERVED_PREFIX):
                err.append(f"{pw}: parameter name must be snake_case, <= 40 chars, no reserved prefix")
            if is_pii(pn):
                err.append(f"{pw}: PII in an event parameter")
            if pt not in TYPES:
                err.append(f"{pw}: type must be one of {sorted(TYPES)}")
            if not isinstance(p.get("required"), bool):
                err.append(f"{pw}: required must be true or false")
            if prop_types.setdefault(pn, pt) != pt:
                err.append(f"{pw}: type {pt}, but {prop_types[pn]} on another event")
            ga4 = p.get("ga4")
            if ga4 is not None:
                if ga4 not in registered:
                    err.append(f"{pw}: ga4 must be dimension or metric")
                elif ga4 == "metric" and pt not in ("integer", "number"):
                    err.append(f"{pw}: a GA4 custom metric must be integer or number")
                else:
                    registered[ga4].add(pn)
            enum = p.get("enum")
            if enum == "screens":
                enum = screens
                if not screens:
                    err.append(f"{pw}: enum: screens but no screens list")
            if enum is not None and not isinstance(enum, list):
                err.append(f"{pw}: enum must be a list or 'screens'")
            elif enum:
                enum_values.update(str(v) for v in enum)
                if any(len(str(v)) > 100 for v in enum):
                    err.append(f"{pw}: enum value > 100 chars")
            if pt == "string" and pn.endswith(("_type", "_source")) and not enum:
                err.append(f"{pw}: *_type / *_source needs an enum")

    if len(events) + len(auto) > LIMITS["events"]:
        err.append(f"{len(events) + len(auto)} event names, Firebase max {LIMITS['events']}")
    for kind, limit in (("dimension", "event_dimensions"), ("metric", "event_metrics")):
        if len(registered[kind]) > LIMITS[limit]:
            err.append(f"{len(registered[kind])} event-scoped custom {kind}s, GA4 max {LIMITS[limit]}")

    if meta.get("core_value_event") and meta["core_value_event"] not in events:
        err.append(f"meta.core_value_event '{meta['core_value_event']}' is not an event")
    key_events = plan.get("key_events") or []
    if len(key_events) > LIMITS["key_events"]:
        err.append(f"{len(key_events)} key events, GA4 max {LIMITS['key_events']}")
    for k in key_events:
        if k not in events and k not in auto:
            err.append(f"key event '{k}' not in events or auto_events")
    if meta.get("core_value_event") and meta["core_value_event"] not in key_events:
        warn.append("core_value_event is not a key event")

    metrics, used = {}, set()
    for m in plan.get("metrics") or []:
        n = m.get("name", "?")
        if n in metrics:
            err.append(f"metric {n}: duplicate")
        metrics[n] = m
        for k in ("question", "definition"):
            if not m.get(k):
                err.append(f"metric {n}: {k} missing")
        if not m.get("events"):
            err.append(f"metric {n}: events missing")
        for e in m.get("events") or []:
            used.add(e)
            if e not in events and e not in auto:
                err.append(f"metric {n}: event '{e}' not in events or auto_events")
    for n in events:
        if n not in used:
            warn.append(f"event {n}: feeds no metric (drop it, or add the metric it answers)")

    external = {m.get("name") for m in plan.get("external_metrics") or []}
    for d in plan.get("dashboards") or []:
        for c in d.get("charts") or []:
            where = f"dashboard {d.get('name', '?')} / {c.get('title', '?')}"
            mn = c.get("metric")
            if mn not in metrics and mn not in external:
                err.append(f"{where}: metric '{mn}' not in metrics or external_metrics")
                continue
            split = c.get("split_by")
            if not split or split in builtin or split in user_props:
                continue
            params = set()
            for e in (metrics.get(mn) or {}).get("events") or []:
                params |= {p.get("name") for p in (events.get(e) or {}).get("properties") or []}
            if split not in params:
                err.append(f"{where}: split_by '{split}' is not a builtin dimension, user property "
                           f"or parameter of the metric's events")
            elif split not in registered["dimension"]:
                err.append(f"{where}: split_by '{split}' must be registered (ga4: dimension) to show in GA4")

    known = (set(events) | auto | all_props | enum_values | set(user_props) | builtin | set(screens))
    return err, warn, events, known


def literals(root):
    found, module = set(), set()
    for f in Path(root).rglob("*"):
        if f.suffix not in SRC_EXT or SKIP_DIRS & set(f.parts) or not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        lits = set(LITERAL.findall(text))
        found |= lits | {c for e in RECOMMENDED for c in sdk_constants(e) if c in text}
        if re.search(r"analytic|track|event", f.name, re.I):
            module |= lits
    return found, module


def check_src(events, known, root):
    err = []
    found, module = literals(root)
    if not found:
        return [f"{root}: no source files found"]
    for n in events:
        if n not in found and not any(c in found for c in sdk_constants(n)):
            err.append(f"{root}: plan event '{n}' not found in code")
    for lit in sorted(module - known):
        if EVENTISH.match(lit):
            err.append(f"{root}: '{lit}' in the analytics module is not in the plan")
    return err


def run(plan, srcs=()):
    err, warn, events, known = check_plan(plan)
    for s in srcs:
        err += check_src(events, known, s)
    return err, warn


def selftest():
    import copy
    import tempfile
    here = Path(__file__).parent
    template = load(str(here / "tracking-plan-template.yaml"))
    err, warn = run(template)
    assert not err and not warn, (err, warn)
    by_name = lambda plan, n: next(e for e in plan["events"] if e["name"] == n)

    bad = copy.deepcopy(template)
    by_name(bad, "onboarding_step_completed")["name"] = "Onboarding.Step"
    by_name(bad, "tutorial_complete")["properties"].append({"name": "email", "type": "string", "required": True})
    push = by_name(bad, "push_permission_answered")["properties"]
    push[1].pop("enum")
    push[0].pop("required")
    by_name(bad, "paywall_viewed")["properties"][0].pop("ga4")
    bad["events"].append(dict(bad["events"][-1], name="session_start"))
    bad["user_properties"].append({"name": "subscription_status_label", "type": "string"})
    bad["metrics"][0]["events"] = ["nope_happened"]
    bad["dashboards"][0]["charts"][0]["split_by"] = "colour"
    err, _ = run(bad)
    text = "\n".join(err)
    for needle in ("name must be snake_case", "PII", "needs an enum", "required must be",
                   "reserved by Firebase", "'nope_happened' not in events", "split_by 'colour'",
                   "split_by 'paywall_source' must be registered", "<= 24 chars"):
        assert needle in text, (needle, text)

    with tempfile.TemporaryDirectory() as d:
        custom = [e["name"] for e in template["events"] if e["name"] not in RECOMMENDED]
        body = "\n".join(f'case {n} = "{n}"' for n in custom) + '\ncase legacy = "old_thing_tapped"\n'
        consts = "".join(f"{sdk_constants(e['name'])[i % 2]}\n" for i, e in enumerate(template["events"])
                         if e["name"] in RECOMMENDED)
        Path(d, "Analytics.swift").write_text(body + consts)
        err, _ = run(template, [d])
        assert err == [f"{d}: 'old_thing_tapped' in the analytics module is not in the plan"], err
        Path(d, "Analytics.swift").write_text(body.replace('"alert_created"', '"x"'))
        err, _ = run(template, [d])
        assert any("'alert_created' not found" in e for e in err), err
        assert any("'sign_up' not found" in e for e in err), err
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    path, srcs, rest = argv[0], [], argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag != "--src" or not rest:
            sys.exit(__doc__)
        srcs.append(rest.pop(0))
    err, warn = run(load(path), srcs)
    for w in warn:
        print("warn ", w)
    for e in err:
        print("ERROR", e)
    print(f"{len(err)} errors, {len(warn)} warnings")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
