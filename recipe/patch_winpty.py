import os
import sys
import time
import glob

def patch_build_rs():
    """Find and patch winpty-rs build.rs to disable ConPTY entirely"""
    
    max_wait = 60
    start_time = time.time()
    
    lib_path = os.environ.get('LIBRARY_LIB', '').replace('\\', '\\\\')
    
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
                    
                    # Only patch if not already patched
                    if 'panic!("NuGet is required' in content and '// PATCHED' not in content:
                        # Disable ConPTY feature entirely
                        new_content = content.replace(
                            '            println!("cargo:rustc-cfg=feature=\\"conpty\\"");',
                            '            // println!("cargo:rustc-cfg=feature=\\"conpty\\""); // PATCHED: Disabled ConPTY'
                        )
                        
                        # Also replace the panic
                        new_content = new_content.replace(
                            'panic!("NuGet is required to build winpty-rs");',
                            f'// PATCHED: Skip NuGet - use only WinPTY\n'
                            f'            println!("cargo:rustc-link-search=native={lib_path}");\n'
                            f'            println!("cargo:rustc-link-lib=winpty");'
                        )
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print("Successfully patched winpty-rs build.rs - ConPTY disabled!")
                        return True
        
        time.sleep(0.5)
    
    print("Warning: Could not find winpty-rs build.rs to patch")
    return False

if __name__ == '__main__':
    patch_build_rs()