@echo off
REM PHPUnit Test Runner for Windows
REM Run this batch file to execute all tests

echo ===============================================
echo Running PHPUnit Tests for REST API
echo ===============================================

REM Change to the project directory
cd /d "%~dp0"

echo.
echo Current directory: %CD%
echo.

REM Run PHPUnit with different output formats
echo [1] Running tests with detailed output...
vendor\bin\phpunit --testdox --colors=never

echo.
echo ===============================================
echo [2] Running tests with summary...
vendor\bin\phpunit --no-coverage

echo.
echo ===============================================
echo [3] Running test execution summary...
php test-execution-summary.php

echo.
echo ===============================================
echo Test execution completed!
echo ===============================================
pause
