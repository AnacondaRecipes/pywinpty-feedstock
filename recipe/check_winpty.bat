@echo on
echo Checking for winpty files...
echo.
echo LIBRARY_BIN=%LIBRARY_BIN%
echo LIBRARY_LIB=%LIBRARY_LIB%
echo.
dir "%LIBRARY_BIN%\winpty*" /b
echo.
dir "%LIBRARY_LIB%\winpty*" /b
echo.
where winpty-agent