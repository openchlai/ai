@echo off
REM Coverage Generation Script for Windows
REM Attempts multiple methods to generate code coverage

echo ===============================================
echo PHPUnit Coverage Generation for REST API
echo ===============================================

cd /d "%~dp0"

echo.
echo Checking available coverage drivers...
echo.

REM Check if Xdebug is available
php -m | findstr /i "xdebug" > nul
if %errorlevel% equ 0 (
    echo [✓] Xdebug extension detected
    goto :xdebug_coverage
) else (
    echo [✗] Xdebug not found
)

REM Check if PCOV is available  
php -m | findstr /i "pcov" > nul
if %errorlevel% equ 0 (
    echo [✓] PCOV extension detected
    goto :pcov_coverage
) else (
    echo [✗] PCOV not found
)

REM Try phpdbg (usually included with PHP)
where phpdbg > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] phpdbg available
    goto :phpdbg_coverage
) else (
    echo [✗] phpdbg not found
)

echo.
echo [WARNING] No code coverage drivers found!
echo.
echo To generate coverage reports, you need one of:
echo 1. Xdebug extension (recommended)
echo 2. PCOV extension (faster)
echo 3. phpdbg (included with PHP)
echo.
echo Installing Xdebug on Windows:
echo 1. Visit: https://xdebug.org/download
echo 2. Find your PHP version with: php -v
echo 3. Download matching Xdebug DLL
echo 4. Add to php.ini: zend_extension=path\to\xdebug.dll
echo 5. Restart web server
echo.
goto :fallback_coverage

:xdebug_coverage
echo.
echo Using Xdebug for coverage generation...
echo.
vendor\bin\phpunit --coverage-html coverage --coverage-text --coverage-clover coverage.xml
goto :coverage_complete

:pcov_coverage
echo.
echo Using PCOV for coverage generation...
echo.
vendor\bin\phpunit --coverage-html coverage --coverage-text --coverage-clover coverage.xml
goto :coverage_complete

:phpdbg_coverage
echo.
echo Using phpdbg for coverage generation...
echo.
phpdbg -qrr vendor\bin\phpunit --coverage-html coverage --coverage-text
goto :coverage_complete

:fallback_coverage
echo.
echo Running tests without coverage...
echo.
vendor\bin\phpunit --testdox --colors=never
echo.
echo Generating estimated coverage report...
php coverage-summary.php
goto :end

:coverage_complete
echo.
echo ===============================================
echo Coverage generation completed!
echo ===============================================
echo.
echo Coverage reports generated:
if exist coverage\index.html (
    echo [✓] HTML Report: coverage\index.html
)
if exist coverage.xml (
    echo [✓] Clover XML: coverage.xml
)
echo [✓] Text Report: displayed above
echo.
echo Opening HTML coverage report...
if exist coverage\index.html (
    start coverage\index.html
)

:end
echo.
echo ===============================================
echo Done!
echo ===============================================
pause
