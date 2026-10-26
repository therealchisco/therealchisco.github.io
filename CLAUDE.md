# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Jekyll blog (Casper theme port) served by GitHub Pages at meet.chisco.org (see `CNAME`; also lists www.chisco.org and chisco.org). No build step in repo, no tests, no package.json — GitHub Pages builds on push to `master`.

## Commands

- Local preview: `bundle exec jekyll serve` (no Gemfile committed; needs `jekyll` + `jekyll-paginate` installed, or add a Gemfile). Output goes to `_site/` (gitignored).

## Architecture

- `_layouts/default.html` is the base; `post.html` and `page.html` extend it. `_includes/` holds pagination, share, disqus partials.
- `index.html` lists posts, paginated via `jekyll-paginate` (`paginate: 15` in `_config.yml`). Pagination only works on `index.html` at root.
- Styles: `assets/css/screen.css` is the Casper theme CSS; `assets/css/main.scss` (front-matter'd, compiled by Jekyll) holds custom overrides and imports `_sass/_syntax.scss` (Rouge highlighting). Put custom CSS in `main.scss`, not `screen.css`.
- `_config.yml`: `disqus-shortname`, `google_analytics` are placeholders; `url`/`baseurl` are empty. Changes to `_config.yml` need a server restart locally.

## Posts

- Files in `_posts/` named `YYYY-MM-DD-slug.md`, front matter: `layout: post`, `title`, `date`, `categories`.
- Posts may embed large inline SVG (hand-drawn pen strokes, e.g. `2022-06-20-tacos.md`) directly in markdown inside `<div class="svg-box">`. Avoid reading/editing those files whole — grep or use line ranges.
- Posts are generated, not hand-written: `scripts/svgz_to_post.py` (CLI) and `scripts/post_studio.py` (drag-and-drop web UI on 127.0.0.1:4720, serves `post_studio.html`) share one pipeline. Write app `.svgz` exports are used as-is (only `<path>` strokes kept); scans (`.jpg/.png/.pdf`) are lighting-flattened, thresholded, despeckled (dot-grid paper) and traced with `potrace` (`brew install potrace`; Pillow + numpy; `pdftoppm` for PDFs). Each drawing is a separate `svg-box` at width 920.
- The studio builds a post from ordered blocks: traced drawings, photos (re-encoded JPEG, EXIF/GPS stripped, saved to `assets/images/posts/<date>-<slug>/NN.jpg`, regenerated on every write) and markdown text.
- Re-running on an existing post replaces only the body; everything above the `<!-- generated body … -->` marker (or, in older posts without it, the first `<div class="svg-box">`) is preserved, so hand-edited front matter, heading and transcript survive.
- Dates are written with the local UTC offset; without it Jekyll skips same-day posts as "future" or files them under the previous day.
- `scripts/`, `CLAUDE.md` and `*.svgz` are excluded from the built site in `_config.yml`.
- Homepage header title/tagline/whoami are traced SVGs in `assets/images/header-*.svg` (text kept as `alt`). Paper background is CSS in `main.scss`.
