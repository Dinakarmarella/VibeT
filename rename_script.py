import os
import sys

old_path = sys.argv[1]
new_path = sys.argv[2]

try:
    os.rename(old_path, new_path)
    print(f"Successfully renamed {old_path} to {new_path}")
except OSError as e:
    print(f"Error renaming directory: {e}")
    sys.exit(1)
