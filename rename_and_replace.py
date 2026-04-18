import os
import hashlib
from pathlib import Path

# ================= 配置区域 =================
# 需要重命名图片的源文件夹
IMAGE_DIR = r"C:\Users\omen\Desktop\Documents\Projects\LCYBlogBak\public\downloaded"
# 包含 Markdown 文件的目标文件夹（脚本会递归搜索其下的所有子文件夹）
MARKDOWN_DIR = r"C:\Users\omen\Desktop\Documents\Projects\LCYBlogBak\2025"
# ============================================

def get_file_md5(file_path):
    """计算文件的MD5哈希值，以此作为新文件名，确保唯一性和标准性"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # 分块读取，防止大文件吃满内存
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    img_dir_path = Path(IMAGE_DIR)
    md_dir_path = Path(MARKDOWN_DIR)

    if not img_dir_path.exists():
        print(f"❌ 找不到图片文件夹: {img_dir_path}")
        return
    if not md_dir_path.exists():
        print(f"❌ 找不到Markdown文件夹: {md_dir_path}")
        return

    mapping = {}
    
    print("🔍 阶段 1/2: 计算图片哈希并重命名...")
    for img_path in img_dir_path.iterdir():
        if img_path.is_file():
            old_name = img_path.name
            ext = img_path.suffix.lower()
            
            # 计算文件真实内容的哈希值 (32位MD5)
            file_hash = get_file_md5(img_path)
            new_name = f"{file_hash}{ext}"
            
            if old_name == new_name:
                continue # 如果已经是哈希命名了，则跳过
            
            new_path = img_dir_path / new_name
            mapping[old_name] = new_name
            
            # 执行文件重命名
            if not new_path.exists():
                img_path.rename(new_path)
            else:
                # 💡 进阶处理：如果哈希计算出的新文件已存在，说明有两张内容完全一样的重复图片
                # 直接将旧名字映射到已存在的哈希文件名上，并删除这份多余的文件
                print(f"  ⚠️ 发现重复图片: 将 {old_name[:20]}... 映射到已存在的 {new_name} 并删除源冗余文件")
                img_path.unlink()

    if not mapping:
        print("✅ 检查完毕，没有需要重命名的图片。")
        return
        
    print(f"✅ 成功生成 {len(mapping)} 个文件名映射字典。")
    
    # 💡 安全策略：将旧文件名按照长度从长到短排序
    # 这样可以防止出现"包含关系"的文件名被错误部分替换（严格一一对应）
    sorted_mapping = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)

    print("\n🔍 阶段 2/2: 递归扫描 Markdown 文件并严格替换链接...")
    md_files = list(md_dir_path.rglob("*.md"))
    modified_count = 0

    for md_path in md_files:
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            is_modified = False
            
            # 遍历映射字典，执行精确文本替换
            for old_name, new_name in sorted_mapping:
                if old_name in new_content:
                    new_content = new_content.replace(old_name, new_name)
                    is_modified = True
            
            # 只有发生替换时，才写回文件，减少对文件系统修改时间的干扰
            if is_modified:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified_count += 1
                # 打印相对路径，方便查看
                print(f"  📝 成功修复引用: {md_path.relative_to(md_dir_path)}")
                
        except UnicodeDecodeError:
            print(f"  ❌ 编码错误，跳过该文件 (请确保是UTF-8编码): {md_path.name}")
        except Exception as e:
            print(f"  ❌ 处理文件 {md_path.name} 时发生错误: {e}")

    print(f"\n🎉 任务完成！总计扫描了 {len(md_files)} 个 .md 文件，实际修改并修复了其中 {modified_count} 个文件的链接。")

if __name__ == "__main__":
    main()