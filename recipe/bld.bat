@echo on

REM Set environment
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM First, trigger cargo to download dependencies
echo Downloading dependencies...
%PYTHON% -c "import subprocess; subprocess.run(['cargo', 'fetch', '--manifest-path=Cargo.toml'], cwd=r'%CD%')"

REM Now find and patch the winpty-rs build.rs
echo Patching winpty-rs build.rs...
for /r "%USERPROFILE%\.cargo\registry\src" %%f in (winpty-rs-1.0.4\build.rs) do (
    if exist "%%f" (
        echo Found build.rs at %%f
        powershell -Command "$content = Get-Content '%%f' -Raw; $content = $content -replace 'panic!\(\"NuGet is required to build winpty-rs\"\);', 'println!(\"cargo:rustc-link-search=native=%LIBRARY_LIB:\=\\%\"); println!(\"cargo:rustc-link-lib=winpty\");'; Set-Content '%%f' $content"
        echo Patched successfully
    )
)

REM Now build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1