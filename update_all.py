"""
完整更新流程脚本
按顺序执行：增量导入 → Emoji转换 → Timeline导出 → 换行修复 → 构建验证
"""
import subprocess
import sys
import os

STEPS = [
    ("增量导入", "python incremental_import.py"),
    ("Emoji 转换", "python replace_emoji.py"),
    ("Timeline 导出", "python generate_timeline.py"),
    ("换行修复", "python fix_linebreaks.py"),
    ("构建验证", "npx vitepress build"),
]

def run_step(name, cmd):
    print(f"\n{'='*60}")
    print(f"[{name}]")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    if result.returncode != 0:
        print(f"\n[错误] {name} 失败！退出码: {result.returncode}")
        sys.exit(1)
    print(f"[完成] {name}")

if __name__ == "__main__":
    print("QQ空间说说完整更新流程")
    print("="*60)
    
    for name, cmd in STEPS:
        run_step(name, cmd)
    
    print(f"\n{'='*60}")
    print("全部完成！")
    print("="*60)
    print("\n下一步:")
    print("  git add . && git commit && git push")
