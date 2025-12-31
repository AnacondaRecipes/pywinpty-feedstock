@echo on

REM Set environment
set "PATH=%LIBRARY_BIN%;%PATH%"
set "LIB=%LIBRARY_LIB%;%LIB%"

REM Download winpty-rs source
cargo download winpty-rs==1.0.4 --extract --output winpty-rs-local

REM Patch the build.rs
powershell -Command ^
  "$file = 'winpty-rs-local\winpty-rs-1.0.4\build.rs'; ^
   $content = Get-Content $file -Raw; ^
   $content = $content -replace 'panic!\(\"NuGet is required to build winpty-rs\"\);', 'println!(\"cargo:rustc-link-search=native=%LIBRARY_LIB:\=\\%\"); println!(\"cargo:rustc-link-lib=winpty\");'; ^
   Set-Content $file -Value $content -NoNewline"

REM Add patch to Cargo.toml
echo. >> Cargo.toml
echo [patch.crates-io] >> Cargo.toml
echo winpty-rs = { path = "winpty-rs-local/winpty-rs-1.0.4" } >> Cargo.toml

REM Build
%PYTHON% -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1

REM Generate license info
cargo-bundle-licenses --format yaml --output "%SRC_DIR%\THIRDPARTY.yml"
if errorlevel 1 exit 1