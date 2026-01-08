@echo on

REM Change to the pywinpty source directory
cd pywinpty-src

REM Set environment
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1

echo Build completed successfully