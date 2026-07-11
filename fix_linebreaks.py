import re
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = '.'
fixed_count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in ['.git', 'node_modules', '.venv', 'public', 'data']]
    
    for filename in filenames:
        if filename.endswith('.md'):
            filepath = os.path.join(dirpath, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into frontmatter and body
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            
            frontmatter = parts[0] + '---' + parts[1] + '---'
            body = parts[2]
            
            # Find the content section (after TID line)
            lines = body.split('\n')
            new_lines = []
            in_content = False
            changed = False
            
            for i, line in enumerate(lines):
                # Skip empty lines, headers, metadata lines, and image lines
                if (line.strip() == '' or 
                    line.startswith('#') or 
                    line.startswith('**') or 
                    line.startswith('![') or
                    line.startswith('###')):
                    new_lines.append(line)
                    continue
                
                # Check if line already ends with two spaces
                if line.endswith('  '):
                    new_lines.append(line)
                    continue
                
                # Add two spaces for line break
                if line.strip():  # Only add spaces to non-empty lines
                    new_lines.append(line + '  ')
                    changed = True
                else:
                    new_lines.append(line)
            
            if changed:
                new_content = frontmatter + '\n' + '\n'.join(new_lines)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_count += 1
                print(f"Fixed: {filepath}")

print(f"\nTotal fixed: {fixed_count} files")
