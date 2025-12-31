@echo on

REM Set environment
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM Use Cargo's build script override feature
REM This tells Cargo to skip running winpty-rs's build.rs and use these values instead
if not exist .cargo mkdir .cargo
(
echo [target.x86_64-pc-windows-msvc.winpty-rs]
echo rustc-link-search = ["%LIBRARY_LIB:\=/%"]
echo rustc-link-lib = ["winpty"]
echo rustc-cfg = ["feature=\"conpty\""]
) > .cargo\config.toml

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1