# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file static web app (`index.html` plus `robots.txt`) — no build system, no package manager, no tests, no framework. It is a Spanish-language ("Staff Access — Joseph Peguero") tool for managing a roster of people and their Dominican ID documents (`cédula`), selecting a subset for an event, and exporting the selection as text, a PDF (via `window.open` + print), or a ZIP of ID images (via JSZip from CDN).

The site is intentionally non-indexable: `robots.txt` disallows everything and `index.html` sets `noindex,nofollow` meta tags for the major crawlers. Preserve these when editing `<head>`.

## Running it

Open `index.html` directly in a browser, or serve the directory statically (e.g. `python3 -m http.server 8000`). The ZIP export needs network on first load to fetch `jszip` from cdnjs; everything else works offline.

## The 3.4 MB index.html problem

`index.html` is one ~1200-line file, but line 445 alone is ~3.5 MB because `BASE_PEOPLE` is a single-line JSON array containing `data:image/jpeg;base64,...` photos for every baseline person.

Practical consequences for any edit:

- `Read` on the whole file fails with a token-limit error. Read by line range with `offset`/`limit`, and stay away from line 445 unless you specifically need it.
- `sed -n 'N,Mp'` or `grep -n` are the reliable ways to inspect content. Always pipe through `cut -c 1-200` (or similar) when touching the `BASE_PEOPLE` line so you don't dump megabytes into the transcript.
- Never paste a base64 image back through `Edit` — match on a short, unique nearby string instead. If you must rewrite the array, do it programmatically.
- The HTML/CSS lives in lines 1–443, the `<script>` block runs 444–1198. Line 445 = `const BASE_PEOPLE = [...]`. Logical script content actually starts at line 446.

## Architecture

Everything is plain DOM + vanilla JS in one IIFE-free script. The mental model is three lists and a selection set:

- `BASE_PEOPLE` (const, embedded at line 445) — the seeded roster with inline base64 photos.
- `customPeople` — runtime-added entries, persisted to `localStorage` under `jp_staff_custom_v1`.
- `hiddenOriginalIds` (`Set`) — IDs from `BASE_PEOPLE` the user has "deleted"; persisted under `jp_staff_hidden_originals_v1`. Base entries are never destructively removed, only hidden, and can be restored from the Manager → Restore flow.
- `selected` (`Set`) — current selection for export; persisted under `jp_staff_selected_v1`.

Derived views are computed each render: `getVisibleBase()` = base minus hidden, `getAllPeople()` = visible base + custom. Grep these helpers when tracing data flow — most rendering code goes through them.

Render entry points (all DOM-replace, no diffing):

- `renderGrid(filter)` — the main card list (`#grid`), filtered by name/cedula substring.
- `renderManager()` / `renderRestore()` — the management modals.
- `buildPreview()` — formats the export text into `#previewText` based on `currentFormat` (`full` | `short` | `list` | `table`).

Export pipeline:

- Text: `buildPreview()` writes plain text into the DOM; `copyText()` / `shareWA()` read it back out.
- ZIP: `downloadZIP()` uses JSZip, folder `Cedulas_Staff/`, files named `NN_NAME_CEDULA.jpg`, plus a `00_LISTADO.txt` index. `dataURLtoBlob()` converts the embedded base64 photos.
- PDF: `downloadPDF()` opens a new window with self-contained HTML+CSS and triggers `print()` — there is no PDF library, the browser print dialog is the PDF generator.

Modals are static markup in the body (`detailModal`, `previewModal`, `formModal`, `managerModal`, `restoreModal`, `confirmModal`) toggled by adding/removing the `open` class. The global `Escape` handler at the bottom of the script closes all of them.

## Conventions to follow

- All user-facing strings are Spanish (`es-DO` locale). Dates use `toLocaleDateString('es-DO', ...)`.
- `savePerson()` uppercases `name`, `birthplace`, `nationality`, `blood`, `occupation` on save — match this if you add new text fields that should be normalized.
- IDs: base entries use short slugs (e.g. `"leonardo"`); custom entries use `custom_<Date.now()>_<random>`. Never reuse a base ID for a custom record.
- Backup JSON files are versioned: v1 was a bare array of custom people; v2 is `{custom, hidden, version: 2, exported}`. `importCustom()` accepts both — preserve that compatibility if you change the schema, and bump `version` for any new shape.
- `localStorage` keys all end in `_v1`. If you change a stored shape, rename the key (don't silently break existing users' data).
- CSS variables in `:root` (`--gold`, `--bg`, `--card`, etc.) define the dark-gold theme; use them instead of hardcoding colors.
- Errors and confirmations go through `toast(msg, isError)` and `showConfirm(title, message, callback)` — don't introduce `alert()` / `confirm()`.
