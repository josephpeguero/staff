# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page, **client-side-only** web app titled "Staff Access — Joseph Peguero" used to assemble lists of staff (with their Dominican Republic `cédula` or passport) to send to clients for event/venue access. The entire app — markup, styles, embedded image data, and logic — lives in `index.html`. UI copy is in Spanish; keep it that way.

The repo has exactly two tracked files:

- `index.html` — the app (~3.6 MB; the bulk is base64-encoded JPEGs of ID documents embedded directly in the `BASE_PEOPLE` array).
- `robots.txt` — disallows all crawlers. This is deliberate (the page contains PII); preserve the `noindex/nofollow` meta tags in `<head>` as well.

There is no package manager, no build step, no bundler, no test suite, and no linter. JSZip is loaded from a CDN at runtime; everything else is vanilla HTML/CSS/JS.

## Running it

Open `index.html` in a browser, or serve the directory with any static server (e.g. `python3 -m http.server` in the repo root, then open `http://localhost:8000/`). A local server is preferable because some browsers restrict `localStorage` and `FileReader` on `file://`.

The first ZIP export per session needs network access so JSZip can load from the CDN.

## Data model and persistence

Three independent lists merge into the visible grid:

- `BASE_PEOPLE` (hard-coded constant near line 445 of `index.html`) — the seed roster, each entry inlining its photo as a `data:image/jpeg;base64,...` string.
- `customPeople` — persisted to `localStorage` under `jp_staff_custom_v1`, edited via the `+` FAB and the "⚙ Gestionar" modal.
- `hiddenOriginalIds` — tombstones for soft-deleted base entries, persisted under `jp_staff_hidden_originals_v1`. Base people are never mutated or removed from the array; they are filtered out via this set so they can be restored later from the manager modal.

`selected` (the user's current pick) is persisted under `jp_staff_selected_v1`.

`getAllPeople()` is the canonical merge: `[...BASE_PEOPLE.filter(not hidden), ...customPeople]`. Most code paths should go through it (or `getPerson(id)`, `isCustom(id)`, `isOriginal(id)`) rather than reaching into the underlying arrays directly.

When adding or modifying fields on a person record, mirror the shape used in `BASE_PEOPLE` so the same render/export code path works for both base and custom entries: `id, name, cedula, doc_type, passport?, birthdate, birthplace, nationality, sex, blood, civil, occupation, expiration, image_b64`.

## Image handling

Uploaded photos are read with `FileReader`, drawn onto a `<canvas>`, downscaled so the longest edge is ≤1200 px, and re-encoded as JPEG at quality `0.82` (`handleImageUpload`). The resulting data URL is what gets stored — keep this compression step intact when touching upload code, because `localStorage` quotas are tight and the app already surfaces a `QuotaExceededError` toast in `saveCustom`.

## Export pipeline

`buildPreview()` produces the text shown in the preview modal and reused by Copy / WhatsApp share, in one of four formats keyed by `currentFormat`: `full`, `short`, `list`, `table`. If you add a new format, add a `.fmt-btn[data-fmt=...]` in the preview modal and a matching branch in `buildPreview()`.

- `downloadZIP()` uses JSZip to bundle each selected person's image plus a `00_LISTADO.txt` index into `Staff_Cedulas_<date>_<n>pers.zip`.
- `downloadPDF()` opens a new window with an inline-styled HTML document and invokes `print()`; the user "saves as PDF" from the browser dialog. There is no PDF library — don't pull one in unless asked.
- `exportCustom()` / `importCustom()` produce a JSON backup `{custom, hidden, version: 2, exported}`. The importer also accepts v1 (a bare array of custom people) — preserve that fallback.

## Editing conventions

- All user-supplied strings rendered into HTML go through `escapeHtml()`. The image grid, manager list, and detail modal all rely on it; don't switch to `innerHTML` with raw user input.
- Filenames derived from names go through `sanitize()` (NFD-strip diacritics, non-alphanumeric → `_`, uppercase).
- Toasts (`toast(msg, isError?)`) are the standard feedback channel — prefer them over `alert()`.
- Modal show/hide is done by toggling the `open` class on `.modal-bg`; the global `Escape` handler closes all of them.
- The styling palette (`--gold`, `--bg`, `--card`, etc.) is declared once in `:root`. Reuse those variables rather than hard-coding hex values.

## Sensitive data

`index.html` contains real names, ID numbers, and photographs. Treat changes that would expose or duplicate this data (logging, network calls, third-party embeds, new crawlable assets) with care, and don't remove the `robots.txt` disallow or the `noindex` meta tags without explicit instruction.
