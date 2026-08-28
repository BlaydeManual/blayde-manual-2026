#!/usr/bin/env python3
"""
Blayde Manual -- manifest structure checker.

checker.py validates a contributed *photo*. This validates a change to
*manifest.json* itself -- a moved bbox, a changed status, an edited
edition label. Those changes currently get zero automated checking:
validate-photo.yml only triggers on paths under images/**. A hand-edited
or malformed manifest.json PR passes CI today with nothing looking at
it at all.

Only checks things a machine can judge fairly: structural validity,
bbox coordinates actually inside the page they claim to be on, no two
entries claiming the same procedure_id. It never judges whether a bbox
is well-*framed* -- that's the same human call review-panel.js's compare
tool already makes, this just catches broken data before a human's time
gets spent on it.

Exit code 0 = all checks passed. Non-zero = at least one hard-fail.
"""
import json
import sys
from pathlib import Path


def bbox_of(entry):
    return entry.get("pixel_bbox") or entry.get("bbox")


def check_manifest(manifest_path):
    results = {"file": str(manifest_path), "hard_fails": [], "warnings": [], "info": {}}
    p = Path(manifest_path)

    try:
        text = p.read_text()
    except FileNotFoundError:
        results["hard_fails"].append(f"file not found: {p}")
        return results

    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as e:
        results["hard_fails"].append(f"not valid JSON: {e}")
        return results

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        results["hard_fails"].append("no 'entries' list at the top level")
        return results

    results["info"]["entry_count"] = len(entries)
    geometry = manifest.get("page_geometry", {})

    seen_ids = {}
    for i, entry in enumerate(entries):
        where = f"entries[{i}]"
        pid = entry.get("procedure_id")
        page = entry.get("page")

        if not pid:
            results["hard_fails"].append(f"{where}: missing procedure_id")
            continue
        where = f"'{pid}'"

        if pid in seen_ids:
            results["hard_fails"].append(
                f"{where}: duplicate procedure_id (also at entries[{seen_ids[pid]}])"
            )
        else:
            seen_ids[pid] = i

        if not isinstance(page, int) or page < 1:
            results["hard_fails"].append(f"{where}: page must be a positive integer, got {page!r}")
            continue

        bbox = bbox_of(entry)
        if bbox is None:
            # Comment-type issues legitimately have no bbox -- see
            # review-panel.js's issue_type handling. Only flag entries
            # that look like they're supposed to have one.
            if entry.get("status") not in ("excluded_false_positive",):
                results["warnings"].append(f"{where}: no pixel_bbox/bbox (ok if this is a comment-only entry)")
            continue

        if not (isinstance(bbox, list) and len(bbox) == 4):
            results["hard_fails"].append(f"{where}: bbox must be [x0, y0, x1, y1], got {bbox!r}")
            continue

        x0, y0, x1, y1 = bbox
        if x0 >= x1 or y0 >= y1:
            results["hard_fails"].append(
                f"{where}: bbox has zero or negative area ({bbox})"
            )

        geo = geometry.get(str(page))
        if geo:
            width = geo.get("composite_width_px")
            height = geo.get("composite_height_px")
            if width and (x0 < 0 or x1 > width):
                results["hard_fails"].append(
                    f"{where}: bbox x-range {x0}-{x1} falls outside page {page}'s width ({width}px)"
                )
            if height and (y0 < 0 or y1 > height):
                results["hard_fails"].append(
                    f"{where}: bbox y-range {y0}-{y1} falls outside page {page}'s height ({height}px)"
                )
        else:
            results["warnings"].append(f"{where}: no page_geometry entry for page {page}, can't check bbox is in-bounds")

    return results


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", default="manifest.json", help="path to manifest.json")
    ap.add_argument("--json", action="store_true", help="machine-readable output (used by CI)")
    args = ap.parse_args()

    r = check_manifest(args.manifest)

    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"\n{r['file']}")
        for k, v in r["info"].items():
            print(f"  {k}: {v}")
        for f in r["hard_fails"]:
            print(f"  FAIL: {f}")
        for w in r["warnings"]:
            print(f"  warn: {w}")
        if not r["hard_fails"]:
            print("  -> PASS")

    sys.exit(1 if r["hard_fails"] else 0)


if __name__ == "__main__":
    main()
