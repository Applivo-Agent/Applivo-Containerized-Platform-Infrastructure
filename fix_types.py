import os
import re

def process_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        
        # 1. Replace `Type | None` -> `Optional[Type]`
        # Avoid changing strings or generic things, just handle basic identifiers and nested []
        # Ex: str | None -> Optional[str]
        # Ex: list[str] | None -> Optional[list[str]]
        # We look for something like 'word | None' or 'word[stuff] | None'
        
        def rep_optional(match):
            type_str = match.group(1).strip()
            return f'Optional[{type_str}]'

        content = re.sub(r'([a-zA-Z0-9_\[\]\s]+?)\s*\|\s*None', rep_optional, content)
        
        # 2. Replace Reverse: `None | Type` -> `Optional[Type]`
        def rep_optional_rev(match):
            type_str = match.group(1).strip()
            return f'Optional[{type_str}]'

        content = re.sub(r'None\s*\|\s*([a-zA-Z0-9_\[\]\s]+?)(?=[,\)\n\:]|$)', rep_optional_rev, content)

        # 3. Replace Type1 | Type2 -> Union[Type1, Type2]
        # Only matches words to prevent breaking actual bitwise operators in code
        def rep_union(match):
            t1 = match.group(1).strip()
            t2 = match.group(2).strip()
            # Ignore cases where the left or right side isn't a type (e.g. values, strings)
            if not re.match(r'^[A-Z][a-zA-Z0-9_]*|str|int|float|bool|list|dict|tuple|set|Any|Mapping|Sequence', t1):
                return match.group(0) # skip
            return f'Union[{t1}, {t2}]'

        # Look for Type1 | Type2
        content = re.sub(r'([a-zA-Z0-9_\[\]]+)\s*\|\s*([a-zA-Z0-9_\[\]]+)', rep_union, content)

        if content != original:
            # Add imports if changed
            # Find the first typing import or create one
            lines = content.split('\n')
            has_typing = False
            first_import = -1
            for i, line in enumerate(lines):
                if line.startswith('from typing import'):
                    has_typing = True
                    parts = line.split('import ')[1].split(',')
                    parts = [p.strip() for p in parts if p.strip()]
                    if 'Optional' not in parts and 'Optional' in content:
                        parts.append('Optional')
                    if 'Union' not in parts and 'Union' in content:
                        parts.append('Union')
                    lines[i] = f'from typing import {", ".join(parts)}'
                    break
                if (line.startswith('import ') or line.startswith('from ')) and first_import == -1:
                    first_import = i

            if not has_typing:
                new_imports = []
                if 'Optional' in content: new_imports.append('Optional')
                if 'Union' in content: new_imports.append('Union')
                if new_imports and first_import != -1:
                    lines.insert(first_import, f"from typing import {', '.join(new_imports)}")
                
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"Fixed {path}")
    except Exception as e:
        print(f"Error processing {path}: {e}")

def main():
    root = 'app'
    for dirpath, _, filenames in os.walk(root):
        if 'node_modules' in dirpath or '.venv' in dirpath:
            continue
        for f in filenames:
            if f.endswith('.py'):
                process_file(os.path.join(dirpath, f))

if __name__ == '__main__':
    main()
