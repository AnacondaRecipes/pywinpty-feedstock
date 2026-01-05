@echo on

REM fetch ConPTY binaries (vendored) and extract it's contents
REM CONPTY_VERSION = 1.18.240821001
curl -L -o conpty.nupkg https://github.com/microsoft/terminal/releases/download/v1.23.13503.0/Microsoft.Windows.Console.ConPTY.1.23.251216003.nupkg
if errorlevel 1 (
    echo ERROR: Download ConPTY package failed
    exit 1
)
if not exist conpty.nupkg (
    echo ERROR: conpty.nupkg was not created
    exit 1
)
echo Successfully downloaded ConPTY

mkdir conpty_extracted
REM powershell -Command "Expand-Archive -Path conpty.nupkg -DestinationPath conpty_extracted -Force"
cd conpty_extracted
tar -xf ../conpty.nupkg
if errorlevel 1 (
    echo ERROR: Failed to unpack conpty.nuget
    exit 1
)
cd ..

REM debuggung list contents:
echo Logging extracted contents
dir conpty_extracted /s /b

REM Copy binaries and lib files to target folder
echo Copying required files
copy conpty_extracted\build\native\runtimes\x64\OpenConsole.exe %LIBRARY_BIN%\
copy conpty_extracted\runtimes\win-x64\native\conpty.dll %LIBRARY_BIN%\
copy conpty_extracted\runtimes\win-x64\lib\uap10.0\conpty.lib %LIBRARY_LIB%\

REM Copy to pywinpty's expected location (source_dir/winpty/)
echo Copying to pywinpty expected location...
mkdir winpty
copy conpty_extracted\build\native\runtimes\x64\OpenConsole.exe winpty\
copy conpty_extracted\runtimes\win-x64\native\conpty.dll winpty\
if not exist winpty\OpenConsole.exe exit 1
if not exist winpty\conpty.dll exit 1

REM Copy to winpty-rs's expected location (target/release/)
echo Copying to winpty-rs expected location...
mkdir target\release
copy conpty_extracted\build\native\runtimes\x64\OpenConsole.exe target\release\
copy conpty_extracted\runtimes\win-x64\native\conpty.dll target\release\
copy conpty_extracted\runtimes\win-x64\lib\uap10.0\conpty.lib target\release\

REM Check that everything went correctly
if not exist %LIBRARY_BIN%\OpenConsole.exe exit 1
if not exist %LIBRARY_BIN%\conpty.dll exit 1
if not exist %LIBRARY_LIB%\conpty.lib exit 1
echo ConPTY was successfully installed
echo.

REM Build pywinpty
echo installing winpty:
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1