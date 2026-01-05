@echo on

REM fetch ConPTY binaries (vendored) and extract it's contents
REM CONPTY_VERSION = 1.18.240821001
curl -L -o conpty.nupkg https://www.nuget.org/api/v2/package/Microsoft.Windows.Console.ConPTY/1.18.240821001
powershell -Command "Expand-Archive -Path conpty.nupkg -DestinationPath conpty_extracted -Force"

REM Copy binaries and lib files to target folder
copy conpty_extracted\build\native\runtimes\x64\OpenConsole.exe %LIBRARY_BIN%\
copy conpty_extracted\runtimes\win-x64\native\conpty.dll %LIBRARY_BIN%\
copy conpty_extracted\runtimes\win-x64\lib\uap10.0\conpty.lib %LIBRARY_LIB%\

REM Check that everything went correctly
if not exist %LIBRARY_BIN%\OpenConsole.exe exit 1
if not exist %LIBRARY_BIN%\conpty.dll exit 1
if not exist %LIBRARY_LIB%\conpty.lib exit 1
echo ConPTY was successfully installed

REM Build pywinpty
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1