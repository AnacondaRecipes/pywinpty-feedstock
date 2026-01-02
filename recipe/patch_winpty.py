import os
import sys
import time
import glob

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
                    
                    # Check if we can find the lines to patch
                    if 'cargo:rustc-cfg=feature="conpty"' not in content:
                        print("WARNING: Could not find conpty feature line to patch!")
                        print("File content sample:")
                        print(content[:500])
                        continue
                    
                    if 'panic!("NuGet is required' not in content:
                        print("WARNING: Could not find panic line!")
                        continue
                    
                    print("Patching file...")
                    
                    # Disable ConPTY feature - try multiple patterns
                    new_content = content
                    
                    # Pattern 1: with escaped quotes
                    new_content = new_content.replace(
                        'println!("cargo:rustc-cfg=feature=\\"conpty\\"");',
                        '// println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED'
                    )
                    
                    # Pattern 2: with regular quotes  
                    new_content = new_content.replace(
                        'println!("cargo:rustc-cfg=feature=\"conpty\"");',
                        '// println!("cargo:rustc-cfg=feature=\"conpty\""); // PATCHED'
                    )
                    
                    # Replace the panic
                    new_content = new_content.replace(
                        'panic!("NuGet is required to build winpty-rs");',
                        f'// PATCHED: Skip NuGet\n            println!("cargo:rustc-link-search=native={lib_path}");\n            println!("cargo:rustc-link-lib=winpty");'
                    )
                    
                    if new_content == content:
                        print("ERROR: No changes made to file!")
                        continue
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("Successfully patched winpty-rs build.rs!")
                    
                    # Verify the patch
                    with open(filepath, 'r', encoding='utf-8') as f:
                        verify = f.read()
                    if '// PATCHED' in verify:
                        print("Patch verified!")
                        return True
                    else:
                        print("ERROR: Patch verification failed!")
        
        time.sleep(0.5)
    
    print("Warning: Could not find winpty-rs build.rs to patch within timeout")
    return False

if __name__ == '__main__':
    result = patch_build_rs()
    sys.exit(0 if result else 1)