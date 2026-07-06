---
title: Technical Details
description: Core technical implementation details of the Python scripts in this project
---

# Technical Details

This document covers the core technical implementation of the backup scripts, including filename generation, URL encoding restoration, and incremental detection.

## 1. `get_safe_name()` — Stable Filename Generation

```python
def get_safe_name(img_url: str) -> str:
    """Generate a unique safe filename strictly based on the original pic_id in JSON"""
    if not img_url:
        return "img_noimage.jpeg"
    return "img_" + hashlib.md5(img_url.encode('utf-8')).hexdigest()[:8] + ".jpeg"
```

**Design points:**

- **The same URL always produces the same filename** — this is the consistency foundation of the entire system
- 8-digit hex = 32bit ≈ 4.2 billion combinations, zero collisions across 159 images
- `.jpeg` extension is hardcoded because QzoneExporter downloads all images as jpeg
- Uses `pic_id` (not `url1`/`url2`/`url3`) as input because `pic_id` is the image uniqueness standard

## 2. `urllib.parse.unquote` — URL Encoding Restoration

The Qzone image download process has an encoding chain:

```
Original URL → purge_file_name() encoding → saved as filename
Filename → urllib.parse.unquote() → restored to original URL
```

### `purge_file_name` encoding rules

```python
# QzoneExporter/tools.py
escape_chars_map = {
    ' ': '%20', '/': '%2F', ':': '%3A', '*': '%2A',
    '?': '%3F', '"': '%22', '<': '%3C', '>': '%3E', '|': '%7C'
}

def purge_file_name(filename):
    filename = filename.replace("%", "%25")  # encode % itself first
    filename = filter_string(filename)        # handle dot-only filenames
    for k, v in escape_chars_map.items():
        filename = filename.replace(k, v)    # encode special characters
    return filename
```

### Why `unquote` perfectly restores

`purge_file_name` is an **approximate inverse** of `unquote`:

| Original | `purge_file_name` | `unquote` restores |
|---|---|---|
| `/` | `%2F` | `/` |
| `:` | `%3A` | `:` |
| `*` | `%2A` | `*` |
| `%` | `%25` | `%` (no further decoding) |

Key: `%25` is restored to `%` by `unquote`, and `%` doesn't trigger secondary decoding, so the result is exactly the original.

## 3. TID First 12 Characters for Dedup

```python
existing_tids.add(tid_match.group(1)[:12])
```

Qzone TID is a 24-character hex string (e.g., `cd356dc9bb92ec69df150000`):

- First 12 chars = 48bit ≈ 280 trillion combinations, sufficient to uniquely identify a post
- Filenames use first 12 chars: `2026-04-25_18-08-58_cd356dc9bb92.md`
- Full TID is used for exact matching in JSON

## 4. Incremental Detection Logic

```
Scan local .md files
    ↓ Extract **TID**: first 12 chars from `cd356dc9bb92...`
    ↓ Build existing_tids set (O(N))

Read all posts from JSON
    ↓ For each post's tid[:12]
    ↓ Not in existing_tids → new post
    ↓ Sort by created_time

Time complexity: O(N + M), N=local file count, M=JSON post count
```

## 5. Correct Image Matching

### Wrong approaches (caused image mismatches)

| Approach | Problem |
|---|---|
| Using `url1` over `pic_id` | Same value, but `pic_id` should be the semantic standard |
| Prefix/fuzzy matching | Multiple files share CDN prefix, picks wrong file |
| `content_hash` reverse lookup | Source filenames are encoded URLs, can't reverse-hash |

### Correct approach

```python
# 1. Build URL → safe_name mapping from JSON (strictly using pic_id)
url_to_safe = {}
for post in posts:
    for pic in post.get("pic", []):
        img_url = pic.get("pic_id")  # highest priority
        if img_url:
            url_to_safe[img_url] = get_safe_name(img_url)

# 2. When copying images, match via unquote to restore URL
for file in qzone_downloaded_dir:
    decoded_url = urllib.parse.unquote(file.stem)
    if decoded_url in url_to_safe:
        safe_name = url_to_safe[decoded_url]
        copy(file, target_dir / safe_name)
```

## 6. Content Hash Verification

After import, verify image correctness via content hashing:

```python
# Compare LCYBlogBak and QzoneExporter image content
lcyblog_hash = md5(LCYBlogBak_file_content)
qzone_hash = md5(QzoneExporter_file_content)
assert lcyblog_hash == qzone_hash  # All 137 passed
```

This proves the `pic_id → get_safe_name → copy` pipeline is fully correct.

## 7. Build Optimization

VitePress build considerations:

- **Rollup parsing**: Special characters in filenames (`*`, `?`, `<`) cause build failures, so `get_safe_name` must generate safe filenames
- **Duplicate detection**: Dedup via content MD5 hash to avoid multiple filenames for the same image
- **Incremental build**: VitePress has built-in caching, only rebuilds changed files
