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
