---
title: 技术细节
description: 本项目中 Python 脚本的核心技术实现细节
---


# 技术细节

本文档介绍备份脚本中的核心技术实现，包括文件名生成、URL 编码还原、增量检测等。  

## 1. `get_safe_name()` — 稳定的文件名生成

```python  
def get_safe_name(img_url: str) -> str:  
    """严格根据 JSON 中的原始 pic_id 生成唯一安全文件名"""  
    if not img_url:  
        return "img_noimage.jpeg"  
    return "img_" + hashlib.md5(img_url.encode('utf-8')).hexdigest()[:8] + ".jpeg"  
```  

**设计要点：**

- **同一 URL 永远生成同一文件名**，这是整个系统的一致性基础  
- 8 位 hex = 32bit ≈ 42 亿种组合，当前 159 张图片无碰撞  
- `.jpeg` 后缀硬编码，因为 QzoneExporter 下载的图片都是 jpeg 格式  
- 使用 `pic_id`（而非 `url1`/`url2`/`url3`）作为输入，因为 `pic_id` 是图片的唯一性标准  

## 2. `urllib.parse.unquote` — URL 编码还原

QQ空间图片的下载流程存在一个编码链：  

```  
原始 URL → purge_file_name() 编码 → 存为文件名  
文件名 → urllib.parse.unquote() → 还原为原始 URL  
```  

### `purge_file_name` 的编码规则

```python  
# QzoneExporter/tools.py
escape_chars_map = {  
    ' ': '%20', '/': '%2F', ':': '%3A', '*': '%2A',  
    '?': '%3F', '"': '%22', '<': '%3C', '>': '%3E', '|': '%7C'  
}  

def purge_file_name(filename):  
    filename = filename.replace("%", "%25")  # 先编码 % 本身  
    filename = filter_string(filename)        # 处理纯点文件名  
    for k, v in escape_chars_map.items():  
        filename = filename.replace(k, v)    # 编码特殊字符  
    return filename  
```  

### 为什么 `unquote` 能完美还原

`purge_file_name` 是 `unquote` 的**近似逆操作**：  

| 原始字符 | `purge_file_name` | `unquote` 还原 |  
|---|---|---|  
| `/` | `%2F` | `/` |  
| `:` | `%3A` | `:` |  
| `*` | `%2A` | `*` |  
| `%` | `%25` | `%`（不再继续解码）|  

关键：`%25` 被 `unquote` 还原为 `%`，而 `%` 不会再触发二次解码，所以能精确还原。  

## 3. TID 前12位去重

```python  
existing_tids.add(tid_match.group(1)[:12])  
```  

QQ空间 TID 是 24 位 hex（如 `cd356dc9bb92ec69df150000`）：  

- 前12位 = 48bit ≈ 280 万亿种组合，足以唯一标识一条说说  
- 文件名使用前12位：`2026-04-25_18-08-58_cd356dc9bb92.md`  
- 全量 TID 用于 JSON 中的精确匹配  

## 4. 增量检测的核心逻辑

```  
扫描本地 .md 文件  
    ↓ 提取 **TID**：`cd356dc9bb92...` 中的前12位  
    ↓ 构建 existing_tids 集合（O(N)）  

读取 JSON 所有说说  
    ↓ 对每条 post 的 tid[:12]  
    ↓ 不在 existing_tids 中 → 新说说  
    ↓ 按 created_time 排序  

时间复杂度：O(N + M)，N=本地文件数，M=JSON 说说数  
```  

## 5. 图片匹配的正确做法

### 错误做法（导致图片错位）

| 做法 | 问题 |  
|---|---|  
| 用 `url1` 优先于 `pic_id` | 虽然值相同，但语义上应以 `pic_id` 为准 |  
| 前缀匹配/模糊匹配 | 多个文件共享 CDN 前缀，会选错文件 |  
| 用 `content_hash` 反查源文件 | 源文件名是编码后的 URL，不能用 hash 反查 |  

### 正确做法

```python  
# 1. 从 JSON 构建 URL → safe_name 映射（严格以 pic_id 为准）
url_to_safe = {}  
for post in posts:  
    for pic in post.get("pic", []):  
        img_url = pic.get("pic_id")  # 最高优先级  
        if img_url:  
            url_to_safe[img_url] = get_safe_name(img_url)  

# 2. 复制图片时，通过 unquote 还原 URL 匹配
for file in qzone_downloaded_dir:  
    decoded_url = urllib.parse.unquote(file.stem)  
    if decoded_url in url_to_safe:  
        safe_name = url_to_safe[decoded_url]  
        copy(file, target_dir / safe_name)  
```  

## 6. 内容哈希验证

导入完成后，通过内容哈希验证图片正确性：  

```python  
# 对比 LCYBlogBak 和 QzoneExporter 的图片内容
lcyblog_hash = md5(LCYBlogBak文件内容)  
qzone_hash = md5(QzoneExporter文件内容)  
assert lcyblog_hash == qzone_hash  # 137 张全部通过  
```  

这证明了 `pic_id → get_safe_name → 复制` 的链路完全正确。  

## 7. 构建优化

VitePress 构建时的注意事项：  

- **Rollup 解析**：文件名中的特殊字符（`*`、`?`、`<`）会导致构建失败，所以必须用 `get_safe_name` 生成安全文件名  
- **重复图片检测**：通过内容 MD5 哈希去重，避免同一张图片占用多个文件名  
- **增量构建**：VitePress 内置缓存，只重建变更的文件  

## 8. Qzone Emoji 转换

QQ空间说说中包含专有的 `[em]eXXXXXXX[/em]` 格式表情，需要转换为 Unicode emoji。  

### 数据来源

使用 [QzEmoji](https://github.com/aioqzone/QzEmoji) 项目的 `emoji.db` 数据库（617 个表情映射）。  

### 转换脚本

```python  
import sqlite3  
import re  

# 加载表情映射
conn = sqlite3.connect('data/emoji.db')  
c = conn.cursor()  
c.execute('SELECT eid, text FROM emoji')  
emoji_map = {row[0]: row[1] for row in c.fetchall()}  
conn.close()  

# 正则匹配 [em]eXXXXXXX[/em]
pattern = re.compile(r'\[em\]e(\d+)\[/em\]')  

def replace_emoji(match):  
    eid = int(match.group(1))  
    return emoji_map.get(eid, match.group(0))  # 未找到则保留原标签  

# 批量替换
new_content = pattern.sub(replace_emoji, content)  
```  

### 已知限制

- 数据库仅覆盖 617 个常用表情，部分较新的表情 ID（如 `e400862`、`e400833`）不在其中  
- 未匹配的 `[em]` 标签会保留原样，显示为文本  
- 可通过 `replace_emoji.py` 脚本重新运行替换  
