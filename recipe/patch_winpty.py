import os
import sys
import time
import glob
import re

def patch_build_rs():
    """Find and patch winpty-rs build.rs to disable ConPTY entirely"""
    
    max_wait = 60
    start_time = time.time()
    
    lib_path = os.environ.get('LIBRARY_LIB', '').replace('\\', '\\\\')
    
    print(f"Looking for winpty-rs build.rs to patch...")
    print(f"Library path: {lib_path}")
    
    while time.time() - start_time < max_wait:
        patterns = [
            os.path.join(os.environ.get('BUILD_PREFIX', ''), '.cargo.win', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
            os.path.join(os.environ.get('USERPROFILE', ''), '.cargo', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for filepath in files:
                if os.path.exists(filepath):
                    print(f"Found build.rs at: {filepath}")
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if already patched
                    if '// PATCHED' in content:
                        print("File already patched, skipping")
                        continue
                    
                    # Check if we can find the panic line
                    if 'panic!("NuGet is required' not in content:
                        print("WARNING: panic line not found, skipping")
                        continue
                    
                    print(f"File size: {len(content)} bytes")
                    print("Searching for conpty cfg line...")
                    
                    # Try to find and replace using regex for flexibility
                    original_content = content
                    
                    # Pattern to match the conpty cfg line with any whitespace/quote variations
                    conpty_pattern = r'println!\("cargo:rustc-cfg=feature=\\"conpty\\""\);'
                    if re.search(conpty_pattern, content):
                        print("Found conpty cfg line with escaped quotes!")
                        content = re.sub(
                            conpty_pattern,
                            r'// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED: Disabled',
                            content
                        )
                    
                    # Replace the panic
                    content = content.replace(
                        'panic!("NuGet is required to build winpty-rs");',
                        f'// PATCHED: Skip NuGet\n            println!("cargo:rustc-link-search=native={lib_path}");\n            println!("cargo:rustc-link-lib=winpty");'
                    )
                    
                    if content == original_content:
                        print("ERROR: No changes made!")
                        # Show more context around line 219
                        lines = content.split('\n')
                        if len(lines) > 219:
                            print(f"Content around line 219:")
                            for i in range(max(0, 210), min(len(lines), 230)):
                                print(f"{i}: {lines[i]}")
                        continue
                    
                    # Write the patched content
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("Successfully patched winpty-rs build.rs!")
                    return True
        
        time.sleep(0.5)
    
    print("Warning: Could not patch winpty-rs within timeout")
    return False

if __name__ == '__main__':
    result = patch_build_rs()
    sys.exit(0 if result else 1)