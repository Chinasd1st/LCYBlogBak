"""
QQ空间说说增量导入工具
严格以 JSON 中 pic_id 为图片唯一性标准，通过 URL 解码匹配源文件。
"""

import json
import hashlib
import urllib.parse
import re
import sys
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Dict, List, Set, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# ==================== 配置 ====================
QZONE_SHUOSHUO_DIR = r"C:\Users\omen\Desktop\Documents\Projects\QzoneExporter\3379377613\shuoshuo"
QZONE_DOWNLOADED_DIR = r"C:\Users\omen\Desktop\Documents\Projects\QzoneExporter\3379377613\shuoshuo\downloaded"
LCYBLOG_DIR = r"C:\Users\omen\Desktop\Documents\Projects\LCYBlogBak"
USER_NAME = "绝赞stars我一生之敌"


def get_safe_name(img_url: str) -> str:
    """严格根据 JSON 中的原始 img_url 生成唯一安全文件名"""
    if not img_url:
        return "img_noimage.jpeg"
    return "img_" + hashlib.md5(img_url.encode('utf-8')).hexdigest()[:8] + ".jpeg"


def scan_existing_tids(lcyblog_dir: Path) -> Set[str]:
    """扫描 LCYBlogBak 中已有的说说 TID（前12位）"""
    existing = set()
    for md_file in lcyblog_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'\*\*TID\*\*：`([a-f0-9]+)`', content)
            if m:
                existing.add(m.group(1)[:12])
        except Exception:
            pass
    return existing


def get_all_posts(shuoshuo_dir: Path) -> List[dict]:
    """从 JSON 读取所有说说并去重"""
    all_posts = []
    for jf in shuoshuo_dir.glob("shuoshuo_*.json"):
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for post in data.get("msglist", []):
                all_posts.append(post)
        except Exception as e:
            print("  读取失败: " + jf.name + " " + str(e))

    seen = set()
    unique = []
    for p in all_posts:
        tid = p.get("tid", "")
        if tid and tid not in seen:
            seen.add(tid)
            unique.append(p)
    return unique


def filter_new_posts(all_posts: List[dict], existing_tids: Set[str]) -> List[dict]:
    """过滤出新说说"""
    new = [p for p in all_posts if p.get("tid", "")[:12] not in existing_tids]
    new.sort(key=lambda x: x.get("created_time", 0))
    return new


def build_url_to_safe_mapping(shuoshuo_dir: Path) -> Dict[str, str]:
    """从 JSON 构建 URL → safe_name 映射（严格以 pic_id 为准）"""
    url_to_safe = {}
    for jf in shuoshuo_dir.glob("shuoshuo_*.json"):
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for post in data.get("msglist", []):
                for pic in post.get("pic", []):
                    img_url = (
                        pic.get("pic_id") or pic.get("url1") or
                        pic.get("url2") or pic.get("url3") or
                        pic.get("smallurl")
                    )
                    if img_url and img_url not in url_to_safe:
                        url_to_safe[img_url] = get_safe_name(img_url)
        except Exception:
            pass
    return url_to_safe


def build_content_hash_index(directory: Path) -> Dict[str, str]:
    """构建 content_hash → filename 映射"""
    index = {}
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() in {'.jpeg', '.jpg', '.png', '.gif', '.mp4'}:
            h = hashlib.md5()
            with open(f, 'rb') as fp:
                for chunk in iter(lambda: fp.read(8192), b''):
                    h.update(chunk)
            index[h.hexdigest()] = f.name
    return index


def generate_markdown(post: dict, output_dir: Path) -> None:
    """为单条说说生成 Markdown"""
    created_ts = post.get("created_time")
    if created_ts:
        dt = datetime.fromtimestamp(created_ts)
        year = dt.strftime("%Y")
        month = dt.strftime("%m")
        date_str = dt.strftime("%Y年%m月%d日 %H:%M:%S")
        date_iso = dt.strftime("%Y-%m-%d")
        file_prefix = dt.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        year = month = "0000"
        date_str = "未知时间"
        date_iso = "0000-00-01"
        file_prefix = "0000-00-01_00-00-00"

    target_dir = output_dir / year / month
    target_dir.mkdir(parents=True, exist_ok=True)

    tid = post.get("tid", "unknown")
    md_path = target_dir / (file_prefix + "_" + tid[:12] + ".md")

    content = post.get("content", "").strip()
    source = post.get("source_name", "未知设备")

    md = (
        "---\n"
        "title: " + date_str + " 的说说\n"
        "date: " + date_iso + "\n"
        "description: " + USER_NAME + " QQ空间说说 · " + date_str + "\n"
        "---\n\n"
        "# " + date_str + "\n\n"
        "**发布人**：" + USER_NAME + "  \n"
        "**设备**：" + source + "  \n"
        "**TID**：`" + tid + "`\n\n"
    )

    md += (content if content else "*（纯图片说说）*") + "\n\n"

    pics = post.get("pic", [])
    if pics:
        md += "### 图片\n\n"
        for i, pic in enumerate(pics, 1):
            img_url = (
                pic.get("pic_id") or pic.get("url1") or
                pic.get("url2") or pic.get("url3") or
                pic.get("smallurl")
            )
            if img_url:
                safe_name = get_safe_name(img_url)
                md += "![说说图片 " + str(i) + "](/downloaded/" + safe_name + ")\n\n"

    rt = post.get("rt_con", {})
    if rt and rt.get("content"):
        rt_name = post.get("rt_uinname", "未知")
        md += "**🔁 转发自 " + rt_name + "**\n\n" + rt.get("content") + "\n\n"

    md_path.write_text(md, encoding="utf-8")


def main():
    print("=" * 60)
    print("QQ空间说说增量导入工具")
    print("=" * 60)

    shuoshuo_dir = Path(QZONE_SHUOSHUO_DIR)
    qzone_dl_dir = Path(QZONE_DOWNLOADED_DIR)
    lcyblog_dir = Path(LCYBLOG_DIR)

    # 1. 扫描现有 TID
    print("\n[1/6] 扫描现有说说 TID...")
    existing_tids = scan_existing_tids(lcyblog_dir)
    print("  现有说说数量: " + str(len(existing_tids)))

    # 2. 读取 JSON
    print("\n[2/6] 读取 QzoneExporter 导出的说说...")
    all_posts = get_all_posts(shuoshuo_dir)
    print("  JSON 中说说总数: " + str(len(all_posts)))

    # 3. 过滤新说说
    print("\n[3/6] 过滤新说说...")
    new_posts = filter_new_posts(all_posts, existing_tids)
    print("  新说说数量: " + str(len(new_posts)))
    if not new_posts:
        print("\n没有新说说需要导入！")
        return

    # 4. 构建 URL → safe_name 映射
    print("\n[4/6] 构建 URL → safe_name 映射...")
    url_to_safe = build_url_to_safe_mapping(shuoshuo_dir)
    print("  唯一图片 URL 数量: " + str(len(url_to_safe)))

    # 5. 生成 Markdown
    print("\n[5/6] 生成 Markdown 文件...")
    md_count = 0
    for post in new_posts:
        generate_markdown(post, lcyblog_dir)
        md_count += 1
    print("  生成 " + str(md_count) + " 个 Markdown 文件")

    # 6. 复制新图片（通过 URL 解码匹配源文件）
    print("\n[6/6] 复制新图片...")
    downloaded_dir = lcyblog_dir / "public" / "downloaded"
    downloaded_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    failed = 0

    for f in qzone_dl_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in {'.jpeg', '.jpg', '.png', '.gif'}:
            continue

        # 通过 URL 解码还原原始 URL
        try:
            decoded_url = urllib.parse.unquote(f.stem)
        except Exception:
            failed += 1
            continue

        # 在映射中查找
        if decoded_url not in url_to_safe:
            # 这些是已有说说的图片，跳过
            skipped += 1
            continue

        safe_name = url_to_safe[decoded_url]
        dest = downloaded_dir / safe_name

        if dest.exists():
            skipped += 1
            continue

        copy2(f, dest)
        copied += 1

    print("  复制 " + str(copied) + " 个新图片")
    print("  跳过 " + str(skipped) + " 个已有图片")
    if failed:
        print("  失败 " + str(failed) + " 个文件")

    # 也复制视频
    video_copied = 0
    for f in qzone_dl_dir.iterdir():
        if f.is_file() and f.suffix == '.mp4':
            dest = downloaded_dir / f.name
            if not dest.exists():
                copy2(f, dest)
                video_copied += 1
    if video_copied:
        print("  复制 " + str(video_copied) + " 个视频")

    # 验证
    print("\n" + "=" * 60)
    print("导入完成！验证中...")
    print("=" * 60)

    # 检查所有新 Markdown 中引用的图片是否存在
    all_ok = True
    for post in new_posts:
        created_ts = post.get("created_time")
        if created_ts:
            dt = datetime.fromtimestamp(created_ts)
            file_prefix = dt.strftime("%Y-%m-%d_%H-%M-%S")
        else:
            file_prefix = "0000-00-01_00-00-00"
        tid = post.get("tid", "unknown")
        md_path = lcyblog_dir / dt.strftime("%Y") / dt.strftime("%m") / (file_prefix + "_" + tid[:12] + ".md")

        if not md_path.exists():
            print("  MISSING: " + md_path.name)
            all_ok = False
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for m in re.finditer(r'!\[.*?\]\(/downloaded/(img_[a-f0-9]+\.jpeg)\)', content):
            img_name = m.group(1)
            img_path = downloaded_dir / img_name
            if not img_path.exists():
                print("  MISSING IMAGE: " + img_name + " in " + md_path.name)
                all_ok = False

    if all_ok:
        print("  所有图片验证通过！")

    print("\n下一步:")
    print("  1. 运行 pnpm run dev 预览")
    print("  2. 运行 pnpm run build 检查构建")
    print("  3. git add . && git commit && git push")


if __name__ == "__main__":
    main()
