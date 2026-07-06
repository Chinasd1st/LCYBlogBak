---
title: About This Project
description: Introduction to Lichenyu's Qzone post backup project - a complete backup solution based on QzoneExporter
---

# About This Project

This project is a **complete backup** of **Lichenyu (绝赞stars我一生之敌)**'s Qzone posts (April 2025 – June 2026, 150 posts total).

## Why This Project

Around April 12, 2026, Lichenyu's Qzone appears to have enabled a "visitors can only view posts from the last year" privacy setting, making older posts invisible to non-friends.

To prevent years of precious memories from being lost, the author decided to create a complete local backup and preserve it long-term as a VitePress static site.

The backup now covers **all posts from April 2025 to June 2026** (150 posts total), with support for incremental updates.

All posts are exported as Markdown files, organized by **year/month**, with locally hosted images, and can be directly deployed as a VitePress static site for permanent archival, searching, and reading.

## Technical Foundation

### QzoneExporter

This backup is primarily built using the open-source project **QzoneExporter**:

- **Repository**: https://github.com/wwwpf/QzoneExporter
- **Features**:
  - Export posts, blogs, albums, message boards, and other Qzone data
  - Automatically download images and videos from posts and albums
  - Display exported data as local web pages (timeline style)
  - Support Exif info writeback and other utilities

**License**: GPL-3.0

## Custom Python Scripts

To make the backup more suitable for VitePress, I wrote the following helper scripts:

### 1. Incremental Import Script (`incremental_import.py`)

- Reads all post data from QzoneExporter's `shuoshuo_*.json` files
- Uses `pic_id` from JSON as the image uniqueness standard, generating stable filenames via **MD5 short hash** (`img_xxxxxxxx.jpeg`)
- Restores original URLs from downloaded filenames using `urllib.parse.unquote` for precise JSON matching
- Generates independent `.md` files in **yyyy/mm/** directory structure, each with Front Matter, content, images, and reposts
- Supports incremental import without overwriting existing content

### 2. Image Rename Script (`rename_downloaded_images.py`)

- Batch-renames QzoneExporter's original downloaded files to VitePress-safe paths
- Ensures filenames are **100% consistent** with Markdown references

These scripts are optimized for VitePress's build characteristics (avoiding Rollup parse errors from special characters), with concise, safe, and stable filenames.

## Features

- **Fully Local**: All images are local files, no dependency on Qzone servers
- **Clean Structure**: Automatic year/month categorization for easy browsing
- **Mobile Friendly**: VitePress supports responsive layout and dark mode by default
- **Search**: Quickly find posts containing keywords via site search
- **Maintainable**: New posts can be added incrementally, scripts are reusable

## Acknowledgments

- Thanks to [QzoneExporter](https://github.com/wwwpf/QzoneExporter) for its powerful export capabilities

---

**Disclaimer**:  
This project is for **personal data archival and memories only**, not for any commercial use. All content belongs to the original author (Lichenyu).

If you have questions about the backup scripts, deployment, or post content, feel free to discuss in GitHub Issues.
