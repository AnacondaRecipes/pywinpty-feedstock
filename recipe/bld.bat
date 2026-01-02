@echo on

REM Set environment
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM Start the patcher in background
start /B %PYTHON% "%RECIPE_DIR%\patch_winpty.py"

REM Give it a moment to start
timeout /t 1 /nobreak >nul

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1