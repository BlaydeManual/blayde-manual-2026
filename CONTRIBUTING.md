# Contributing to blayde-manual-2026 -- Blayde Manual

If you're restoring, wrenching on, or documenting a blayde-manual-2026,
your photos here don't just fix a broken manual -- **your GitHub username
gets permanently credited directly on the photo, in the actual PDF**,
every time someone enhances their own legal copy with the Blayde Manual
overlay. That's not a
buried commit in history; it's a visible, permanent "photo: @you" line
under the exact procedure your photo documents, for as long as anyone
uses this manual. If you're a restoration creator building a body of work
around a vehicle, this is a citable, permanent credit -- not a comment
that scrolls off a video description in a week.

## Before you start

1. **Check the gallery** for the procedure you want to shoot: `manifest.json`
   in this repo lists every figure the original manual needs a photo for,
   each with a `procedure_id`. If you're not sure which one matches what
   you're looking at, open an issue or ask -- better to check than guess.
2. **One photo per pull request.** Small, independently-reviewable PRs
   get merged fast, and this repo has no way to choose between several
   photos landing in one PR anyway. A PR bundling many photos means one
   bad one blocks the rest -- don't do that to yourself or the reviewer.

## Photo requirements

Run the checker before you open a PR -- it's the same script CI runs, so
there are no surprises:

```bash
python checker.py your_photo.jpg --manifest manifest.json
```

It checks:
- **Resolution**: at least 1200x900
- **Focus**: not blurry (a real focus-score check, not just "looks fine to me")
- **Zero non-pixel data**: your camera embeds GPS/location, camera model,
  and timestamp by default, and some editors add color profiles or
  comments -- none of it is allowed here (location data especially: this
  project doesn't want anyone able to work out where a contributor's
  vehicle actually lives). The checker can strip all of it for you with
  `--fix`. Credit stays outside the file either way -- it's drawn onto
  the photo fresh, by the site itself, every time someone patches their
  own manual, never baked into what you upload.
- **Filename matches a real `procedure_id`** from `manifest.json`

It won't (and can't) check whether your photo actually shows the right
step correctly -- that's a human reviewer's call, not a machine's.

### The quality bar, the short version

No essay, just the actual bar:
- **Show the thing.** If the bolt, connector, or part the procedure is
  about isn't clearly visible, it doesn't help anyone, even if it's
  technically a sharp photo.
- **In focus, decently lit.** You don't need a studio, you need to be
  able to see what you're looking at.
- **Your own photo, your own vehicle/work.** Not a screenshot from a
  forum post or someone else's video.
- **When in doubt, review it like you'd want yours reviewed.** That's
  the actual standard -- everything above is just what it looks like in
  practice.

## Filename convention

```
<procedure_id>.jpg
```

To get credited (see above -- you want this):

```
<procedure_id>__by_<your-github-username>.jpg
```

Multiple angles of the same procedure are welcome -- there doesn't need to
be one "winning" photo per step:

```
<procedure_id>__by_<your-github-username>__alt2.jpg
```

## Licensing your photo

Every photo needs an explicit license grant -- the PR template has a
checkbox for this, not buried fine print. Photos are contributed under
**CC-BY 4.0**: anyone can use them, they just have to credit you. You're
also confirming it's your own photo (not lifted from a forum post or
someone else's build thread) -- same copyright problem, one layer down,
and it also means you can't be properly credited for someone else's work
anyway.

**Know this before you submit: CC-BY 4.0 is irrevocable.** Once a photo
is merged and used, you can't pull the license back on copies that
already exist -- that's not an oversight, it's what makes an open
license actually safe for anyone to build on. You can always ask to have
a photo removed from the active `images/` folder, and it'll stop being
offered to anyone patching a manual from that point on, but it won't
reach into manuals other people already generated before the removal.
If that tradeoff doesn't sit right with you for a given photo, it's
worth thinking about before you open the PR, not after.

## What review looks like

- **Automated checks** (resolution, blur, EXIF, filename) run in CI on
  every PR -- if you ran the checker locally first, these should never
  surprise you.
- **Human review** confirms the photo actually shows the right procedure.
  If it's good but not quite the featured angle, it's very likely to be
  merged as an alternate rather than rejected outright -- this project
  doesn't do single-canonical-photo-per-procedure.

If you're the one reviewing (any repo maintainer can be), the bar is the
same one contributors are asked to hold themselves to, restated from the
other side: does it show the thing, is it legible, is it plausibly this
person's own photo. Reasonable judgment, not a checklist -- if you'd
merge it into your own manual, merge it.

**Your only real job is deciding whether a submitted photo is good.**
That's it. A short list of things that are explicitly *not* on you, so
you never end up worrying about them:

- **How big this repo gets, or how many photos are in it.** Not your
  problem to manage or plan for.
- **Scaling** -- more contributors, more traffic, more vehicles across
  the project. That's the Blayde Manual team's concern, not a repo
  maintainer's.
- **Whether the whole project succeeds.** You're responsible for this
  one vehicle's photos being good, not for the project's future.
- **The legal/copyright architecture.** Already solved once, at the
  project level (see `LEGAL.md`) -- nothing about that needs
  re-deciding per repo.

If you're only ever doing the one thing above -- looking at a photo and
deciding if it's a good one -- you're doing this job completely right.

## What this project is not

Not affiliated with, endorsed by, or sponsored by the original
manufacturer. This repo never contains the original manual's own scanned
images or text -- only structure (page numbers, figure locations) plus
photos the community has taken and licensed. See the main project's
`LEGAL.md` for the full reasoning if you're curious why the repo is built
this way.
