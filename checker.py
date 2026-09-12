#!/usr/bin/env python3
"""
Blayde Manual -- contribution checker.

Same script runs in two places:
  - locally, before a contributor opens a PR (fast, private feedback)
  - in CI, on the PR (confirms what they already saw -- no surprises)

Only checks things a machine can judge fairly: resolution, blur, EXIF
stripped, filename matches a real procedure_id in the manifest. It never
judges "does this actually show the right procedure" -- that's a human
call, tagged needs-second-opinion, not a hard reject.

Exit code 0 = all checks passed. Non-zero = at least one hard-fail.
"""
import json
import sys
from pathlib import Path

from PIL import Image
import numpy as np

MIN_WIDTH = 1200  # fallback only -- used when a photo's procedure_id has no pixel_bbox/page_geometry to size against (see min_dimensions_for)
MIN_HEIGHT = 900
# Bbox-aware floor's own DPI target -- deliberately HALF of contribute.js's
# own TARGET_DPI (200), and this floor skips that file's 2x HEADROOM
# multiplier entirely. Not an attempt to mirror that formula exactly:
# two independent implementations of the same math, in two different
# languages (this is Python CI, that's browser JS), will drift out of
# sync eventually. Real, confirmed bug this replaces (2026-09-11,
# suzuki-sv650-1999 #17/#19): a flat 1200x900 floor rejected genuine
# high-resolution photos (6000x4000 Sony a6000 originals) that
# contribute.js's own bbox-aware downscale had correctly, deliberately
# sized down for a small procedure's actual on-page footprint (see
# ROADMAP.md's "Repo-size math" entry and web/contribute.js's
# computeTargetLongEdge). Using half the DPI and none of the headroom
# here means contribute.js's real output always clears this floor with
# comfortable margin, so a future constant change on either side
# doesn't immediately start rejecting otherwise-correct submissions.
BBOX_TARGET_DPI = 100
ABS_MIN_DIMENSION = 400  # sanity floor regardless of bbox size -- never accept something smaller than this even for a tiny bbox
BLUR_VARIANCE_FLOOR = 80.0   # Laplacian-variance focus score; below this reads as blurry
MAX_FILE_MB = 15


def min_dimensions_for(procedure_id, manifest):
    """The real resolution floor for one procedure's photo, sized to that
    procedure's actual bbox rather than a flat number -- falls back to
    the flat MIN_WIDTH/MIN_HEIGHT when the manifest, the entry, its
    pixel_bbox, or that page's page_geometry aren't available (an
    add-new-slot proposal with no bbox yet, an older/malformed
    manifest, etc.), same as contribute.js's own computeTargetLongEdge
    falls back to FALLBACK_MAX_DIMENSION_PX in the equivalent case."""
    if not manifest:
        return MIN_WIDTH, MIN_HEIGHT
    entry = next((e for e in manifest.get("entries", []) if e.get("procedure_id") == procedure_id), None)
    if not entry or not entry.get("pixel_bbox"):
        return MIN_WIDTH, MIN_HEIGHT
    geometry = (manifest.get("page_geometry") or {}).get(str(entry.get("page")))
    if not geometry:
        return MIN_WIDTH, MIN_HEIGHT
    x0, y0, x1, y1 = entry["pixel_bbox"]
    scale_x = geometry["composite_width_px"] / geometry["page_width_pt"]
    scale_y = geometry["composite_height_px"] / geometry["page_height_pt"]
    width_pt = (x1 - x0) / scale_x
    height_pt = (y1 - y0) / scale_y
    target_w = (width_pt / 72) * BBOX_TARGET_DPI
    target_h = (height_pt / 72) * BBOX_TARGET_DPI
    return max(ABS_MIN_DIMENSION, round(target_w)), max(ABS_MIN_DIMENSION, round(target_h))


def laplacian_variance(gray_arr):
    # 3x3 discrete Laplacian via manual convolution (no scipy dependency)
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    a = gray_arr.astype(np.float32)
    h, w = a.shape
    out = np.zeros_like(a)
    out[1:-1, 1:-1] = (
        a[0:-2, 1:-1] * k[0, 1]
        + a[1:-1, 0:-2] * k[1, 0]
        + a[1:-1, 1:-1] * k[1, 1]
        + a[1:-1, 2:] * k[1, 2]
        + a[2:, 1:-1] * k[2, 1]
    )
    return out.var()


def check_image(path, expected_id=None, manifest_ids=None, manifest=None):
    results = {"file": str(path), "hard_fails": [], "warnings": [], "info": {}}
    p = Path(path)

    size_mb = p.stat().st_size / (1024 * 1024)
    results["info"]["file_size_mb"] = round(size_mb, 2)
    if size_mb > MAX_FILE_MB:
        results["hard_fails"].append(f"file too large ({size_mb:.1f}MB > {MAX_FILE_MB}MB)")

    try:
        img = Image.open(p)
        img.load()
    except Exception as e:
        results["hard_fails"].append(f"not a readable image: {e}")
        return results

    w, h = img.size
    results["info"]["dimensions"] = f"{w}x{h}"
    min_w, min_h = min_dimensions_for(expected_id, manifest)
    if w < min_w or h < min_h:
        results["hard_fails"].append(f"resolution too low ({w}x{h}, need >= {min_w}x{min_h})")

    # Hard fail on ANY non-pixel data, not just EXIF -- direct instruction:
    # "zero data, only the pixels" (attribution lives outside the image
    # file entirely -- patcher.js draws the credit tag fresh at patch
    # time, never embeds it). img.getexif() alone isn't enough to prove
    # that: confirmed empirically it returns an EMPTY dict for a real
    # JPEG carrying an ICC profile or a comment marker, both real,
    # inspectable metadata getexif() simply doesn't look at. img.info
    # exposes all of it (ICC profiles, comments, PNG text chunks, EXIF),
    # so that's the real surface to check, not just the EXIF-specific one.
    # JFIF_ALLOWED is the exact set PIL itself leaves on a JPEG it just
    # re-saved with zero auxiliary data passed in -- confirmed by
    # actually re-saving a stripped image and inspecting its own
    # info dict, not guessed: universal container bookkeeping (format
    # version, pixel density unit) present on every real JPEG, not
    # identifying information. A clean PNG has no such floor -- any
    # info key at all is real, removable data.
    JFIF_ALLOWED = {"jfif", "jfif_version", "jfif_unit", "jfif_density"}
    extra_keys = [k for k in img.info.keys() if k not in JFIF_ALLOWED]
    if extra_keys:
        results["info"]["non_pixel_data"] = extra_keys
        results["hard_fails"].append(
            f"file carries non-pixel data ({', '.join(extra_keys)}) -- strip it before upload (try --fix)"
        )

    gray = np.array(img.convert("L").resize((min(w, 1000), int(min(w, 1000) * h / w))))
    variance = laplacian_variance(gray)
    results["info"]["focus_score"] = round(float(variance), 1)
    if variance < BLUR_VARIANCE_FLOOR:
        results["hard_fails"].append(
            f"image looks blurry/out of focus (focus score {variance:.1f}, need >= {BLUR_VARIANCE_FLOOR})"
        )

    if expected_id:
        stem = p.stem
        if manifest_ids is not None and expected_id not in manifest_ids:
            results["hard_fails"].append(
                f"'{expected_id}' is not a known procedure_id in this vehicle's manifest.json"
            )
        elif stem.split("__")[0] != expected_id and stem != expected_id:
            results["warnings"].append(
                f"filename '{stem}' doesn't cleanly match expected procedure_id '{expected_id}' "
                "-- ok if this is an alternate angle (use '<procedure_id>__altN.jpg')"
            )

    return results


def strip_exif_inplace(path):
    """Convenience: decode to pure pixels and re-save with zero auxiliary
    data (EXIF, ICC profile, comments, PNG text chunks) -- contributor can
    run --fix. Already produces exactly what check_image's own allowlist
    expects, confirmed by re-checking the result immediately after."""
    img = Image.open(path)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    clean.save(path)


def load_manifest(manifest_path):
    if not manifest_path or not Path(manifest_path).exists():
        return None
    return json.loads(Path(manifest_path).read_text())


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", help="image file(s) to check")
    ap.add_argument("--manifest", help="path to manifest.json for procedure_id validation")
    ap.add_argument("--fix", action="store_true", help="strip EXIF in place on warning")
    ap.add_argument("--json", action="store_true", help="machine-readable output (used by CI)")
    args = ap.parse_args()

    manifest = load_manifest(args.manifest)
    manifest_ids = {e["procedure_id"] for e in manifest["entries"]} if manifest else None
    all_results = []
    any_hard_fail = False

    for img_path in args.images:
        p = Path(img_path)
        expected_id = p.stem.split("__")[0]
        r = check_image(p, expected_id=expected_id, manifest_ids=manifest_ids, manifest=manifest)
        if args.fix and any("non-pixel data" in f for f in r["hard_fails"]):
            strip_exif_inplace(p)
            r = check_image(p, expected_id=expected_id, manifest_ids=manifest_ids, manifest=manifest)
            r["info"]["fixed"] = "non-pixel data stripped by --fix"
        all_results.append(r)
        if r["hard_fails"]:
            any_hard_fail = True

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        for r in all_results:
            print(f"\n{r['file']}")
            for k, v in r["info"].items():
                print(f"  {k}: {v}")
            for f in r["hard_fails"]:
                print(f"  FAIL: {f}")
            for w in r["warnings"]:
                print(f"  warn: {w}")
            if not r["hard_fails"]:
                print("  -> PASS (ready to submit)")

    sys.exit(1 if any_hard_fail else 0)


if __name__ == "__main__":
    main()
