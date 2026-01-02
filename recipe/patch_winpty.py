import os
import sys
import time
import glob

def patch_build_rs():
    """Find and patch winpty-rs build.rs to skip NuGet check"""
    
    # Wait for cargo to extract winpty-rs
    max_wait = 60  # seconds
    start_time = time.time()
    
    lib_path = os.environ.get('LIBRARY_LIB', '').replace('\\', '\\\\')
    
    while time.time() - start_time < max_wait:
        # Search in conda build env cargo cache
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
                    
                    if 'panic!("NuGet is required' in content:
                        # Replace the panic with link directives
                        # DON'T set conpty_local - let it use native Windows ConPTY
                        new_content = content.replace(
                            'panic!("NuGet is required to build winpty-rs");',
                            f'// Use native ConPTY instead of downloading via NuGet\n'
                            f'            println!("cargo:rustc-link-search=native={lib_path}");\n'
                            f'            println!("cargo:rustc-link-lib=winpty");'
                        )
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print("Successfully patched build.rs!")
                        return True
        
        time.sleep(0.5)
    
    print("Warning: Could not find winpty-rs build.rs to patch")
    return False

if __name__ == '__main__':
    patch_build_rs()