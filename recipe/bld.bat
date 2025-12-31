@echo on

REM Set environment for winpty
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM Create a .cargo/config.toml that sets environment for all cargo builds
if not exist .cargo mkdir .cargo
(
echo [env]
echo PATH = { value = "%PATH%", force = true }
echo LIB = { value = "%LIB%", force = true }
) > .cargo\config.toml

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1