import os
import sys
import time
import glob
import re

def patch_build_rs_continuous():
    """Continuously patch winpty-rs build.rs whenever it appears"""
    
    lib_path = os.environ.get('LIBRARY_LIB', '').replace('\\', '\\\\')
    max_runtime = 600  # Run for max 10 minutes
    start_time = time.time()
    
    print(f"Starting continuous patcher for winpty-rs...")
    patched_files = set()
    
    while time.time() - start_time < max_runtime:
        patterns = [
            os.path.join(os.environ.get('BUILD_PREFIX', ''), '.cargo.win', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
            os.path.join(os.environ.get('USERPROFILE', ''), '.cargo', 'registry', 'src', '*', 'winpty-rs-1.0.4', 'build.rs'),
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for filepath in files:
                # Skip if we already patched this exact file
                if filepath in patched_files:
                    continue
                    
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Skip if already patched
                    if '// PATCHED' in content:
                        patched_files.add(filepath)
                        continue
                    
                    # Check if needs patching
                    if 'panic!("NuGet is required' not in content:
                        continue
                    
                    print(f"\n[{time.strftime('%H:%M:%S')}] Found unpatched file: {filepath}")
                    
                    # Disable ALL conpty features
                    modified = False
                    
                    # Replace ALL occurrences of conpty cfg
                    pattern_conpty = r'println!\("cargo:rustc-cfg=feature=\\"conpty\\""\);'
                    matches = len(re.findall(pattern_conpty, content))
                    if matches > 0:
                        print(f"  Disabling {matches} conpty feature line(s)")
                        content = re.sub(
                            pattern_conpty,
                            r'// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED',
                            content
                        )
                        modified = True
                    
                    # Disable conpty_local
                    pattern_local = r'println!\("cargo:rustc-cfg=feature=\\"conpty_local\\""\);'
                    if re.search(pattern_local, content):
                        print(f"  Disabling conpty_local feature")
                        content = re.sub(
                            pattern_local,
                            r'// println!("cargo:rustc-cfg=feature=\\"conpty_local\\""); // PATCHED',
                            content
                        )
                        modified = True
                    
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
                        patched_files.add(filepath)
                        print("  ✓ Patched successfully!")
        
        time.sleep(0.3)
    
    print(f"\nPatcher finished. Patched {len(patched_files)} file(s) total.")
    return len(patched_files) > 0

if __name__ == '__main__':
    patch_build_rs_continuous()