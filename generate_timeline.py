"""
生成 timeline.json 供 Timeline 组件使用
扫描所有说说 Markdown，提取元数据
"""
import re, json
from pathlib import Path
from datetime import datetime

LCYBLOG_DIR = Path(r"C:\Users\omen\Desktop\Documents\Projects\LCYBlogBak")
output = []

for md_file in sorted(LCYBLOG_DIR.rglob("*.md")):
    if md_file.name in ("index.md", "intro.md", "tech.md", "AGENTS.md"):
        continue
    if md_file.parent.name in ("en", ".vitepress", "node_modules"):
        continue

    try:
        content = md_file.read_text(encoding="utf-8")
    except:
        continue

    # Extract frontmatter
    fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        continue

    # Extract TID
    tid_match = re.search(r'\*\*TID\*\*：`([a-f0-9]+)`', content)
    if not tid_match:
        continue
    tid = tid_match.group(1)

    # Extract timestamp from filename
    ts_match = re.search(r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})', md_file.name)
    if ts_match:
        dt = datetime(int(ts_match.group(1)), int(ts_match.group(2)), int(ts_match.group(3)),
                      int(ts_match.group(4)), int(ts_match.group(5)), int(ts_match.group(6)))
        ts = int(dt.timestamp())
    else:
        ts = 0

    # Extract content (after the metadata block)
    body = content.split("\n\n", 3)[-1] if "\n\n" in content else ""

    # Remove image markdown
    body_clean = re.sub(r'### 图片\n*', '', body)
    body_clean = re.sub(r'!\[.*?\]\(.*?\)', '', body_clean).strip()

    # Truncate
    if len(body_clean) > 150:
        body_clean = body_clean[:150] + "..."

    # Extract source
    source_match = re.search(r'\*\*设备\*\*：(.+?)(?:\s{2}|\n)', content)
    source = source_match.group(1) if source_match else ""

    # Extract images
    images = re.findall(r'/downloaded/(img_[a-f0-9]+\.jpeg)', content)

    output.append({
        "tid": tid[:12],
        "ts": ts,
        "content": body_clean,
        "source": source,
        "images": images,
        "hasImages": len(images) > 0,
        "file": str(md_file.relative_to(LCYBLOG_DIR))
    })

output.sort(key=lambda x: x["ts"])

# Write to public/
out_path = LCYBLOG_DIR / "public" / "timeline.json"
out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"生成 timeline.json: {len(output)} 条说说")
