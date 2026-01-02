import os
import sys
import time
import glob
import re

def patch_build_rs():
    """Find and patch winpty-rs build.rs"""
    
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
                    
                    # Find line numbers for debugging
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'rustc-cfg=feature' in line and 'conpty' in line:
                            print(f"Line {i}: {line.strip()}")
                        if 'NuGet is required' in line:
                            print(f"Line {i}: {line.strip()}")
                    
                    # Do the replacement - search for any variation
                    modified = False
                    
                    # Try multiple patterns for the conpty line
                    patterns_to_try = [
                        (r'println!\("cargo:rustc-cfg=feature=\\"conpty\\""\);', 
                         r'// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED'),
                        (r"println!\('cargo:rustc-cfg=feature=\"conpty\"'\);",
                         r"// println!('cargo:rustc-cfg=feature=\"conpty\"'); // PATCHED"),
                        # Raw string search
                        ('println!("cargo:rustc-cfg=feature=\\"conpty\\"");',
                         '// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED'),
                    ]
                    
                    for pattern, replacement in patterns_to_try:
                        if re.search(pattern, content):
                            print(f"Matched pattern: {pattern}")
                            content = re.sub(pattern, replacement, content)
                            modified = True
                            break
                    
                    # Replace panic
                    if 'panic!("NuGet is required to build winpty-rs");' in content:
                        content = content.replace(
                            'panic!("NuGet is required to build winpty-rs");',
                            f'// PATCHED\n            println!("cargo:rustc-link-search=native={lib_path}");\n            println!("cargo:rustc-link-lib=winpty");'
                        )
                        modified = True
                    
                    if modified:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("✓ Patched successfully!")
                        return True
                    else:
                        print("✗ No modifications made")
        
        time.sleep(0.5)
    
    return False

if __name__ == '__main__':
    patch_build_rs()