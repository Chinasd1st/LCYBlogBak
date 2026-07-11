import sqlite3
import re
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connect to emoji database
conn = sqlite3.connect('data/emoji.db')
c = conn.cursor()

# Build emoji mapping
c.execute('SELECT eid, text FROM emoji')
emoji_map = {row[0]: row[1] for row in c.fetchall()}
conn.close()

print(f"Loaded {len(emoji_map)} emoji mappings")

# Pattern to match [em]eXXXXXXX[/em]
pattern = re.compile(r'\[em\]e(\d+)\[/em\]')

def replace_emoji(match):
    eid = int(match.group(1))
    return emoji_map.get(eid, match.group(0))  # Return original if not found

# Process all markdown files
root_dir = '.'
replaced_count = 0
file_count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Skip .git and node_modules
    dirnames[:] = [d for d in dirnames if d not in ['.git', 'node_modules', '.venv']]
    
    for filename in filenames:
        if filename.endswith('.md'):
            filepath = os.path.join(dirpath, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file contains [em] tags
            if '[em]' in content:
                new_content = pattern.sub(replace_emoji, content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # Count replacements
                    matches = pattern.findall(content)
                    replaced_count += len(matches)
                    file_count += 1
                    print(f"Updated: {filepath} ({len(matches)} emojis)")

print(f"\nTotal: Updated {file_count} files, replaced {replaced_count} emoji tags")
