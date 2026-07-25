#!/usr/bin/env python3
"""undervolt_outlier_flag.py - integrity gate for the crowdsourced undervolt dataset.

The undervolt-results database (data/undervolt_results.json) is moderated by git: contributors
open a pull request adding a row, and this script is the automated first check. It flags rows
that are implausible or statistically anomalous so a human reviewer's attention goes to the
right place. A flagged row still merges (transparency) but is held OUT of the clean on-site
table by the shortcode until reviewed.

TWO LAYERS (see ADR-style note below):
  1. HARD PLAUSIBILITY BOUNDS (always on, vendor-aware) - catch impossible/typo submissions
     regardless of how many rows exist: a positive AMD offset, 350 W "saved", a 5000 MHz clock.
  2. PER-CARD STATISTICAL OUTLIER (dormant until a card has >=MIN_STAT rows) - on the fields that
     ARE comparable within one GPU model (voltage/offset/fps). NOT per-vendor: clock, power, and
     temp are not comparable across different card models, so cross-model stats would false-flag
     a high-clocking card. Per-card stats activate exactly when crowdsourcing makes them meaningful.

Modes:
  --check   report flagged rows; exit 1 if any row is flagged (CI / PR gate). Does not write.
  --apply   write flagged / flag_reason back into the JSON (sets flagged=false + reason='' on clean rows).
  --self-test  inject known-bad rows and assert each is caught (RED/GREEN; proves the gate is load-bearing).

Stdlib only.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "undervolt_results.json"

REQUIRED = ["id", "gpu", "vendor", "method", "setting", "source_type", "source_url", "date"]
MIN_STAT = 5           # per-card rows needed before statistical flagging turns on
STAT_K = 4.0           # flag |x - median| > STAT_K * MAD (robust; MAD must be > 0)
STAT_FIELDS = ["voltage_mv", "offset_mv", "fps_delta_pct"]   # comparable WITHIN one card model

# Hard plausibility bounds. Vendor-aware where the field's meaning differs by vendor.
def bound_reasons(r):
    """Return a list of hard-bound violation strings for one row (empty == plausible)."""
    out = []
    v = r.get("vendor")

    def numck(field, lo, hi):
        x = r.get(field)
        if x is None:
            return
        if not isinstance(x, (int, float)):
            out.append("%s is not numeric (%r)" % (field, x))
        elif x < lo or x > hi:
            out.append("%s=%s outside plausible [%s, %s]" % (field, x, lo, hi))

    # voltage_mv: NVIDIA curve target (~700-1100) OR AMD RDNA3 absolute max (~950-1250) -> union
    numck("voltage_mv", 700, 1250)
    # offset_mv: AMD negative offset only
    off = r.get("offset_mv")
    if off is not None:
        if not isinstance(off, (int, float)):
            out.append("offset_mv not numeric (%r)" % off)
        elif off > 0:
            out.append("offset_mv=%s is positive (undervolt offsets are negative)" % off)
        elif off < -250:
            out.append("offset_mv=%s below plausible -250 mV" % off)
    numck("clock_mhz", 800, 4200)
    # power_limit_pct: NVIDIA is % of stock (~40-115); AMD is a delta (~-60..+20)
    pl = r.get("power_limit_pct")
    if pl is not None:
        if not isinstance(pl, (int, float)):
            out.append("power_limit_pct not numeric (%r)" % pl)
        elif v == "NVIDIA" and (pl < 40 or pl > 115):
            out.append("power_limit_pct=%s outside NVIDIA [40, 115]" % pl)
        elif v == "AMD" and (pl < -60 or pl > 20):
            out.append("power_limit_pct=%s outside AMD delta [-60, 20]" % pl)
    numck("power_saved_w", 0, 250)   # real undervolt savings top out ~135 W (5090); >250 W is a typo/error
    numck("temp_drop_c", 0, 40)
    numck("fps_delta_pct", -25, 25)
    numck("stability_hours", 0, 1000)

    # AMD without any voltage control, or NVIDIA using an AMD-style offset, is suspicious
    if v == "AMD" and r.get("offset_mv") is None and r.get("voltage_mv") is None:
        out.append("AMD row has neither offset_mv nor voltage_mv")
    if v == "NVIDIA" and r.get("offset_mv") is not None:
        out.append("NVIDIA row uses offset_mv (NVIDIA undervolts via a V/F-curve target voltage)")
    return out


def schema_reasons(r):
    out = []
    for k in REQUIRED:
        if not r.get(k):
            out.append("missing required field '%s'" % k)
    su = r.get("source_url", "")
    if su and not (su.startswith("http") or su.startswith("/")):
        out.append("source_url is not a resolvable URL or site path: %r" % su)
    return out


def stat_reasons(rows):
    """Per-CARD statistical outliers. rows == full list; returns {id: [reasons]}."""
    by_card = {}
    for r in rows:
        by_card.setdefault(r.get("gpu"), []).append(r)
    flags = {}
    for gpu, group in by_card.items():
        if len(group) < MIN_STAT:
            continue
        for field in STAT_FIELDS:
            vals = [(r["id"], r[field]) for r in group
                    if isinstance(r.get(field), (int, float))]
            if len(vals) < MIN_STAT:
                continue
            nums = [x for _, x in vals]
            med = statistics.median(nums)
            mad = statistics.median([abs(x - med) for x in nums])
            if mad <= 0:
                continue
            for rid, x in vals:
                if abs(x - med) > STAT_K * mad:
                    flags.setdefault(rid, []).append(
                        "%s=%s is a per-card outlier vs %s median %s (MAD %s)"
                        % (field, x, gpu, med, mad))
    return flags


def hard_flags(rows):
    """Schema + hard-plausibility violations. BLOCKING: typos, impossible values, missing source."""
    out = {}
    for r in rows:
        reasons = schema_reasons(r) + bound_reasons(r)
        if reasons:
            out[r["id"]] = reasons
    return out


def evaluate(rows):
    """All flags (hard + statistical) merged - used to mark rows held OUT of the on-site table."""
    flagged = {k: list(v) for k, v in hard_flags(rows).items()}
    for rid, reasons in stat_reasons(rows).items():
        flagged.setdefault(rid, []).extend(reasons)
    return flagged


def load():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    return d, d.get("results", [])


def run_check():
    _, rows = load()
    hard = hard_flags(rows)
    stat = stat_reasons(rows)
    print("undervolt outlier check: %d rows | %d hard violation(s), %d statistical outlier(s)"
          % (len(rows), len(hard), len(stat)))
    for rid, reasons in hard.items():
        print("  BLOCK %s:" % rid)
        for why in reasons:
            print("        - %s" % why)
    for rid, reasons in stat.items():
        print("  WARN  %s (plausible but anomalous - held for review, does not block merge):" % rid)
        for why in reasons:
            print("        - %s" % why)
    if hard:
        print("  -> blocking: fix the hard violations above before this PR can merge.")
        return 1
    print("  -> ok: no schema/plausibility violations.%s"
          % (" statistical outliers are warnings only." if stat else " all rows plausible + sourced."))
    return 0


def run_apply():
    d, rows = load()
    flagged = evaluate(rows)
    for r in rows:
        if r["id"] in flagged:
            r["flagged"] = True
            r["flag_reason"] = "; ".join(flagged[r["id"]])
        else:
            r["flagged"] = False
            r["flag_reason"] = ""
    DATA.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print("undervolt outlier apply: wrote %d rows, %d flagged" % (len(rows), len(flagged)))
    return 0


def self_test():
    """Prove each layer is load-bearing: a clean row passes, and each injected defect is caught."""
    fails = []
    clean = {"id": "clean", "gpu": "RTX 4090", "vendor": "NVIDIA", "method": "MSI Afterburner V/F curve",
             "setting": "925 mV @ 2700 MHz", "voltage_mv": 925, "offset_mv": None, "clock_mhz": 2700,
             "power_limit_pct": 90, "power_saved_w": 90, "temp_drop_c": 9, "fps_delta_pct": 0,
             "stability_hours": None, "source_type": "community-consensus",
             "source_url": "https://example.com/x", "date": "2026-07-24"}
    if evaluate([clean]):
        fails.append("CLEAN-FALSE-POSITIVE: a plausible sourced row was flagged: %s" % evaluate([clean]))

    bad_cases = {
        "positive AMD offset": {**clean, "id": "b1", "vendor": "AMD", "voltage_mv": None,
                                "offset_mv": 50, "power_limit_pct": -10},
        "impossible power saved": {**clean, "id": "b2", "power_saved_w": 350},
        "missing source": {**clean, "id": "b3", "source_url": ""},
        "clock typo": {**clean, "id": "b4", "clock_mhz": 27000},
        "NVIDIA using offset": {**clean, "id": "b5", "offset_mv": -80},
        "fps out of range": {**clean, "id": "b6", "fps_delta_pct": 60},
    }
    for name, row in bad_cases.items():
        if not evaluate([row]):
            fails.append("MISS: '%s' defect was NOT flagged (bound is not load-bearing)" % name)

    # per-card statistical layer: 5 tight rows + 1 wild -> the wild one flags; fewer than 5 -> dormant
    base = [{**clean, "id": "s%d" % i, "voltage_mv": 925 + i} for i in range(5)]
    wild = {**clean, "id": "swild", "voltage_mv": 1180}
    st = stat_reasons(base + [wild])
    if "swild" not in st:
        fails.append("STAT-MISS: a per-card voltage outlier among >=5 rows was not flagged")
    if stat_reasons(base[:3] + [wild]):
        fails.append("STAT-OVEREAGER: statistical flagging fired on a group smaller than MIN_STAT")

    if fails:
        sys.stderr.write("[undervolt-outlier SELF-TEST RED]\n")
        for f in fails:
            sys.stderr.write("   - %s\n" % f)
        return 2
    print("undervolt-outlier SELF-TEST: GREEN (clean passes; all 6 hard defects + per-card stat caught; small-group dormant)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--self-test", action="store_true", dest="selftest")
    a = ap.parse_args(argv)
    if a.selftest:
        return self_test()
    if a.apply:
        return run_apply()
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
