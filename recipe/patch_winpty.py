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
    
    print(f"Looking for winpty-rs build.rs...")
    
    while time.time() - start_time < max_wait:
        patterns = [
            os.path.join(os.environ.get('BUILD_PREFIX', ''), '.cargo.win', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
            os.path.join(os.environ.get('USERPROFILE', ''), '.cargo', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for filepath in files:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Skip if already patched
                    if '// PATCHED' in content:
                        continue
                    
                    # Must have the panic line
                    if 'panic!("NuGet is required' not in content:
                        continue
                    
                    print(f"\nFound file: {filepath}")
                    print(f"File size: {len(content)} chars")
                    
                    # Find all lines with conpty feature
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'rustc-cfg=feature' in line and 'conpty' in line:
                            print(f"Line {i}: {line.strip()}")
                        if 'NuGet is required' in line:
                            print(f"Line {i}: {line.strip()}")
                    
                    # Disable ALL conpty feature settings using regex
                    modified = False
                    
                    # Replace ALL occurrences of the conpty cfg line
                    pattern = r'println!\("cargo:rustc-cfg=feature=\\"conpty\\""\);'
                    matches = len(re.findall(pattern, content))
                    if matches > 0:
                        print(f"Found {matches} conpty feature line(s)")
                        content = re.sub(
                            pattern,
                            r'// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED: Disabled ConPTY',
                            content
                        )
                        modified = True
                    
                    # Also disable conpty_local if it appears
                    pattern_local = r'println!\("cargo:rustc-cfg=feature=\\"conpty_local\\""\);'
                    if re.search(pattern_local, content):
                        print(f"Found conpty_local feature line")
                        content = re.sub(
                            pattern_local,
                            r'// println!("cargo:rustc-cfg=feature=\\"conpty_local\\""); // PATCHED: Disabled',
                            content
                        )
                        modified = True
                    
                    # Replace panic
                    if 'panic!("NuGet is required to build winpty-rs");' in content:
                        content = content.replace(
                            'panic!("NuGet is required to build winpty-rs");',
                            f'// PATCHED: Skip NuGet\n            println!("cargo:rustc-link-search=native={lib_path}");\n            println!("cargo:rustc-link-lib=winpty");'
                        )
                        modified = True
                    
                    if modified:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("✓ Patched successfully - ConPTY fully disabled!")
                        return True
                    else:
                        print("✗ No modifications made")
        
        time.sleep(0.5)
    
    return False

if __name__ == '__main__':
    patch_build_rs()