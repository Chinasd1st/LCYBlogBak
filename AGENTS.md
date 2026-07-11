# AGENTS.md - LCYBlogBak 项目规范

## 项目概述

VitePress 个人博客，自动备份 QQ空间说说（来自用户 李晨煜，QQ: 3379377613）。

## 关键路径

| 路径 | 说明 |
|---|---
|  
| `YYYY/MM/*.md` | 说说 Markdown，文件名格式 `YYYY-MM-DD_HH-MM-SS_{TID前12位}.md` |  
| `public/downloaded/` | 图片/视频，命名格式 `img_{MD5前8位}.jpeg` |  
| `incremental_import.py` | 增量导入脚本 |  

## 根因分析：图片错位问题

### 现象

导入说说后，图片显示为错误内容（如推文截图代替原图），或构建报错找不到图片文件。  

### 根因

**QzoneExporter 下载的文件名与 JSON 中的 URL 使用不同的编码方案，但二者可以通过 `urllib.parse.unquote` 完美还原。**

具体数据流：  

```  
JSON pic_id (原始URL)  
  ↓  get_safe_name() = md5(url)[:8]  
  ↓  
Markdown 引用: /downloaded/img_XXXXXXXX.jpeg  

下载文件名: purge_file_name(url) + ".jpeg"  
  ↓  urllib.parse.unquote(文件名stem)  
  ↓  
还原得到: 原始URL (与 pic_id 完全一致)  
```  

关键事实：  
- JSON 中 `pic_id`、`url1`、`url2`、`url3` 四个字段值完全相同（206字符）  
- 下载文件名经 `purge_file_name()` 编码后存储，`unquote` 后可还原为原始 URL  
- **`pic_id` 就是下载时使用的原始 URL，是图片的唯一性标准**  

### 错误做法（导致图片错位）

1. **用 `url1` 优先于 `pic_id`** — 虽然值相同，但语义上应以 `pic_id` 为准  
2. **前缀匹配/模糊匹配** — 多个文件共享 CDN 前缀 `https%3A%2F%2Fphotogzmaz...`，前缀匹配会选错文件  
3. **用 `content_hash` 做源文件匹配** — 源文件名是编码后的 URL，不能用 hash 反查  

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
    decoded_url = urllib.parse.unquote(file.stem)  # 还原原始 URL  
    if decoded_url in url_to_safe:  
        safe_name = url_to_safe[decoded_url]  
        copy(file, target_dir / safe_name)  
```  

## get_safe_name 规范

```python  
def get_safe_name(img_url: str) -> str:  
    """严格根据 JSON 中的原始 pic_id 生成唯一安全文件名"""  
    if not img_url:  
        return "img_noimage.jpeg"  
    return "img_" + hashlib.md5(img_url.encode('utf-8')).hexdigest()[:8] + ".jpeg"  
```  

**同一 URL 永远生成同一文件名**，保证 Markdown 引用与实际文件一一对应。

## 增量导入流程（incremental_import.py）

1. 扫描 `public/downloaded/` 和 `YYYY/MM/*.md` 中已有的 TID  
2. 读取 QzoneExporter JSON，过滤出新说说  
3. 为新说说生成 Markdown（`pic_id` → `get_safe_name` → 图片引用）  
4. 从 QzoneExporter `downloaded/` 复制新图片（`unquote(filename)` → 匹配 `pic_id` → 复制为 `safe_name`）  
5. 验证所有图片引用存在  

## QzoneExporter 导出命令

```powershell  
# 必须同时指定 --shuoshuo 和 --download，否则只下载不导出
python exporter.py --shuoshuo --download  
```  

**重要：不加参数运行 `python exporter.py` 只执行下载，不导出说说 JSON。**

### 一年限制

QQ空间对外部查看者有**一年时间限制**：非好友只能看到最近一年的说说。主页显示的说说总数（如 266）是全部说说数，但 API 实际只返回最近一年的数据（如 ~130 条）。  

导出器会在 API 返回空 msglist 时自动停止，并打印警告：  
```  
not get correct shuoshuo, get: 134, should get: 266  
```  

这是正常行为，不影响已有数据的完整性。  

### 图片下载

图片需要在导出时通过 `--download` 参数一起下载。如果先运行 `--shuoshuo` 再单独运行 `--download`，需要确保两次使用相同的 cookie。  

## 构建命令

```powershell  
# Windows PowerShell
$env:CI="true"; pnpm run build  
# 或直接
npx vitepress build  
```  

## 注意事项

- QzoneExporter cookie 位于 `exporter.py` 第 903 行，过期后需更新  
- JSON 中 `to_download.txt` 的 URL 列与文件名列相同，均经 `purge_file_name()` 编码  
- `img_34a50be2.jpeg`（2025-10-11）为已知缺失，QzoneExporter 中也不存在  
- 导出后需手动检查图片是否完整（`incremental_import.py` 会报告 MISSING IMAGE）  

## 更新说说时的必须步骤

每次导入新说说后，必须执行以下两个步骤：  

### 1. Emoji 转换

QQ空间说说中的 `[em]eXXXXXXX[/em]` 标签需转换为 Unicode emoji：  

```powershell  
python replace_emoji.py  
```  

- 数据库：`data/emoji.db`（来自 [QzEmoji](https://github.com/aioqzone/QzEmoji)，617 个表情）  
- 脚本会遍历所有 `.md` 文件，将 `[em]eXXXXXXX[/em]` 替换为对应 emoji  
- 未匹配的标签保留原样  

### 2. Timeline 导出

更新 `public/timeline.json` 供首页和时间线页面使用：  

```powershell  
python generate_timeline.py  
```  

- 扫描所有 `YYYY/MM/*.md` 文件  
- 提取时间、内容、图片、设备信息  
- 输出 `public/timeline.json`  

### 完整更新流程

```powershell  
# 1. 导出新说说
cd C:\Users\omen\Desktop\Documents\Projects\QzoneExporter  
python exporter.py --shuoshuo --download  

# 2. 增量导入
python incremental_import.py  

# 3. Emoji 转换
python replace_emoji.py  

# 4. Timeline 导出
python generate_timeline.py  

# 5. 构建验证
npx vitepress build  
```  
