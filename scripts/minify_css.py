import re
import sys
from pathlib import Path

def minify_css(css_content):
    # Remove CSS comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove extra spaces around braces and colons/semicolons
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r'\s*([\{\};:,])\s*', r'\1', css_content)
    # Strip leading/trailing whitespaces
    return css_content.strip()

def main():
    root = Path(__file__).resolve().parent.parent
    css_dir = root / 'app' / 'static' / 'css'
    
    for filename in ['custom.css', 'dark.css']:
        file_path = css_dir / filename
        if not file_path.exists():
            print(f"Skipping {filename}: not found.")
            continue
            
        print(f"Minifying {filename}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        minified = minify_css(content)
        
        min_filename = filename.replace('.css', '.min.css')
        min_file_path = css_dir / min_filename
        with open(min_file_path, 'w', encoding='utf-8') as f:
            f.write(minified)
            
        orig_size = len(content)
        min_size = len(minified)
        saved = orig_size - min_size
        pct = (saved / orig_size) * 100 if orig_size > 0 else 0
        print(f"  Saved to {min_filename}: {orig_size} B -> {min_size} B ({saved} B saved, {pct:.1f}%)")

if __name__ == '__main__':
    main()
