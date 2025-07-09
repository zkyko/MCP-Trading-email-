"""
This script updates all imports from 'email' package to 'email_utils'
after renaming the folder to avoid conflicts with Python's built-in email module.
"""

import os
import re
import sys

def update_imports(directory="."):
    """
    Find all Python files in the directory and update imports
    from 'email.' to 'email_utils.'
    """
    pattern = re.compile(r'from\s+email\.([^\s]+)\s+import|import\s+email\.([^\s]+)')
    files_changed = 0
    lines_changed = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file contains imports from our email module
                if 'from email.' in content or 'import email.' in content:
                    new_content = re.sub(r'from email\.', 'from email_utils.', content)
                    new_content = re.sub(r'import email\.', 'import email_utils.', new_content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        files_changed += 1
                        # Count how many lines were changed
                        lines_changed += sum(1 for line in content.splitlines() 
                                           if 'from email.' in line or 'import email.' in line)
                        print(f"Updated imports in: {file_path}")
    
    return files_changed, lines_changed

if __name__ == "__main__":
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    print(f"Updating imports from 'email' to 'email_utils' in Python files...")
    files_changed, lines_changed = update_imports(directory)
    print(f"Done! Updated {lines_changed} imports in {files_changed} files.")
    
    # Check if the email directory still exists
    if os.path.exists("email"):
        print("\n⚠️ Warning: 'email' directory still exists.")
        print("After verifying that all imports are updated, you may want to remove it.")
        print("Example command: rm -rf email  # or manually delete the folder")
