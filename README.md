# blayde-manual-2026 -- Blayde Manual

**Just want an updated manual, not the GitHub side of things?** Go to
**[blaydemanual.com](https://blaydemanual.com)** instead -- pick your
vehicle, patch your own PDF, no account or git knowledge needed. This
repo is the real data behind that site, useful if you want to see the
source, browse contributor history, or open a PR by hand.

A community-maintained, ever-improving version of the blayde-manual-2026
service manual. The original manual's own photos are old, low-resolution
scans that have gotten worse with every re-scan over the years -- this
project replaces them with real photos from people actually doing the
work, one procedure at a time, credited by name.

**Not affiliated with, endorsed by, or sponsored by the original
manufacturer.** Informational, community-sourced documentation --
verify safety-critical specs (torque, brake, fuel system) against an
authoritative source before relying on this document. See the parent
project's `LEGAL.md` for the full reasoning behind how this repo is built.

## Get an updated manual

1. Get your own copy of the blayde-manual-2026 service manual PDF
   (this repo never contains the original manual itself -- see below).
2. Run the patcher against your copy + this repo's approved photos to get
   a manual with the current photos merged in.
3. Already have a Blayde Manual PDF from before? Feed that back in instead
   of the original -- it's recognized automatically and only patches
   what's new since your last copy.

## Contribute a photo

**Your GitHub username gets permanently credited on the photo, in the
actual PDF, every time someone enhances their own legal copy with the
Blayde Manual overlay.** See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full guide -- filename
convention, photo requirements, and how review works.

## What this repo actually contains

- `manifest.json` -- structure only: page numbers, section headings, and
  where each figure belongs. No copyrighted content from the original
  manual, ever -- see [LEGAL.md](https://github.com/BlaydeManual/blayde-manual/blob/main/LEGAL.md)
  in the main tooling repo for why.
- `images/<procedure_id>/` -- community-contributed photos, each licensed
  CC-BY 4.0 by its contributor.

This repo will never contain the original manual's own scanned pages,
photos, or text, in any branch or commit history.
