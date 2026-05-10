@echo off
rem ============================================================================
rem  PDF Text Extractor - one-command Windows .exe builder
rem
rem  Produces a single self-contained PDFTextExtractor.exe (no Python needed
rem  on the client machine). Output: windows\dist\PDFTextExtractor.exe
rem
rem  Usage (from a regular cmd.exe or PowerShell):
rem      cd windows
rem      build_app.bat
rem
rem  First run is slow (downloads PyQt6 + PyMuPDF + PyInstaller into .venv\).
rem  Subsequent rebuilds use the cached venv.
rem ============================================================================
setlocal EnableDelayedExpansion

rem ----- Resolve paths --------------------------------------------------------
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%SCRIPT_DIR%\.."
set "SPEC=%SCRIPT_DIR%\PDFTextExtractor_win.spec"
set "VENV=%SCRIPT_DIR%\.venv"
set "DIST=%SCRIPT_DIR%\dist"
set "WORK=%SCRIPT_DIR%\build"

if not exist "%SPEC%" (
    echo [ERROR] Spec file not found: %SPEC%
    exit /b 1
)

rem ----- Pick a Python --------------------------------------------------------
rem Prefer 3.12, then 3.11, 3.10, then whatever `python` resolves to.
set "PYTHON="
for %%P in (py-3.12 py-3.11 py-3.10) do (
    where %%P >nul 2>nul && (
        set "PYTHON=py -%%P:py-=%"
        goto :py_done
    )
)
where python >nul 2>nul && (
    for /f "tokens=2 delims= " %%V in ('python --version 2^>^&1') do set "PYVER=%%V"
    set "PYTHON=python"
)
:py_done

if not defined PYTHON (
    echo [ERROR] Python 3.10, 3.11, or 3.12 not found.
    echo         Install from https://www.python.org/downloads/ and re-run.
    exit /b 1
)
echo [OK] Using Python via: %PYTHON%

rem ----- Create / refresh venv ------------------------------------------------
rem A venv hard-codes its install path. If the project moved, rebuild it.
set "STALE=0"
if exist "%VENV%\pyvenv.cfg" (
    findstr /C:"%VENV%" "%VENV%\pyvenv.cfg" >nul 2>nul || set "STALE=1"
)
if "%STALE%"=="1" (
    echo [INFO] Rebuilding stale venv...
    rmdir /s /q "%VENV%"
)
if not exist "%VENV%" (
    echo [INFO] Creating build venv at %VENV%
    %PYTHON% -m venv "%VENV%" || exit /b 1
)

set "VPY=%VENV%\Scripts\python.exe"
set "VPIP=%VENV%\Scripts\pip.exe"

rem ----- Install build deps ---------------------------------------------------
echo [INFO] Upgrading pip + installing build deps...
"%VPY%" -m pip install --quiet --upgrade pip wheel || exit /b 1
"%VPY%" -m pip install --quiet --upgrade ^
    "PyMuPDF>=1.24.0" ^
    "PyQt6>=6.6.0" ^
    "pyinstaller>=6.6.0" || exit /b 1

rem ----- Clean previous build -------------------------------------------------
echo [INFO] Cleaning previous build...
if exist "%DIST%" rmdir /s /q "%DIST%"
if exist "%WORK%" rmdir /s /q "%WORK%"

rem ----- Run PyInstaller ------------------------------------------------------
echo [INFO] Building PDFTextExtractor.exe... (this takes a minute)
pushd "%SCRIPT_DIR%"
"%VPY%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --workpath "%WORK%" ^
    --distpath "%DIST%" ^
    "%SPEC%"
set "BUILD_RC=%ERRORLEVEL%"
popd

rem ----- Cleanup intermediate folder -----------------------------------------
if exist "%WORK%" rmdir /s /q "%WORK%"

if not "%BUILD_RC%"=="0" (
    echo [ERROR] PyInstaller failed with exit code %BUILD_RC%.
    exit /b %BUILD_RC%
)

set "EXE=%DIST%\PDFTextExtractor.exe"
if not exist "%EXE%" (
    echo [ERROR] Build finished but %EXE% was not produced.
    exit /b 1
)

rem ----- Report ---------------------------------------------------------------
for %%I in ("%EXE%") do set "SIZE=%%~zI"
set /a "SIZE_MB=SIZE/1048576"

echo.
echo -----------------------------------------------------------------
echo [OK] Build succeeded
echo      .exe:  %EXE%
echo      size:  %SIZE_MB% MB
echo -----------------------------------------------------------------
echo.
echo Next steps:
echo   * Test it:        "%EXE%"
echo   * Ship it:        zip the .exe and upload to a GitHub Release.
echo   * Clients run it: double-click PDFTextExtractor.exe.
echo                     SmartScreen may show "Windows protected your PC"
echo                     -- click "More info" -> "Run anyway" the first time
echo                     (one-time bypass for unsigned apps).
echo.
endlocal
