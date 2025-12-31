@echo on

REM Create a temp dir without spaces
set WINPTY_TEMP=%SRC_DIR%\winpty_temp
mkdir "%WINPTY_TEMP%"

REM Copy winpty files there
copy "%LIBRARY_BIN%\winpty-agent.exe" "%WINPTY_TEMP%\"
copy "%LIBRARY_BIN%\winpty.dll" "%WINPTY_TEMP%\"
copy "%LIBRARY_LIB%\winpty.lib" "%WINPTY_TEMP%\"

REM Add to PATH at the front
set "PATH=%WINPTY_TEMP%;%PATH%"
set "LIB=%WINPTY_TEMP%;%LIB%"

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Cleanup
rmdir /s /q "%WINPTY_TEMP%"

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1