if "%ARCH%" == "32" (set PLATFORM=x86) else (set PLATFORM=x64)
"%PYTHON%" setup.py install --single-version-externally-managed --record record.txt
if errorlevel 1 exit 1
