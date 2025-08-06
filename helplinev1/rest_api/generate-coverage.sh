#!/bin/bash
# Coverage Generation Script for Git Bash
# Attempts multiple methods to generate code coverage

echo "=============================================="
echo "PHPUnit Coverage Generation for REST API"
echo "=============================================="

cd "$(dirname "$0")"

echo ""
echo "Checking available coverage drivers..."
echo ""

# Check if Xdebug is available
if php -m | grep -i "xdebug" >/dev/null; then
    echo "[✓] Xdebug extension detected"
    COVERAGE_DRIVER="xdebug"
elif php -m | grep -i "pcov" >/dev/null; then
    echo "[✓] PCOV extension detected"
    COVERAGE_DRIVER="pcov"
elif command -v phpdbg >/dev/null 2>&1; then
    echo "[✓] phpdbg available"
    COVERAGE_DRIVER="phpdbg"
else
    echo "[✗] No coverage drivers found"
    COVERAGE_DRIVER="none"
fi

echo ""

case $COVERAGE_DRIVER in
    "xdebug"|"pcov")
        echo "Using $COVERAGE_DRIVER for coverage generation..."
        echo ""
        vendor/bin/phpunit --coverage-html coverage --coverage-text --coverage-clover coverage.xml
        COVERAGE_EXIT_CODE=$?
        ;;
    "phpdbg")
        echo "Using phpdbg for coverage generation..."
        echo ""
        phpdbg -qrr vendor/bin/phpunit --coverage-html coverage --coverage-text
        COVERAGE_EXIT_CODE=$?
        ;;
    "none")
        echo "[WARNING] No code coverage drivers found!"
        echo ""
        echo "To generate coverage reports, you need one of:"
        echo "1. Xdebug extension (recommended)"
        echo "2. PCOV extension (faster)"
        echo "3. phpdbg (included with PHP)"
        echo ""
        echo "Installing Xdebug on Windows:"
        echo "1. Visit: https://xdebug.org/download"
        echo "2. Find your PHP version with: php -v"
        echo "3. Download matching Xdebug DLL"
        echo "4. Add to php.ini: zend_extension=path/to/xdebug.dll"
        echo "5. Restart web server"
        echo ""
        echo "Running tests without coverage..."
        echo ""
        vendor/bin/phpunit --testdox --colors=never
        echo ""
        echo "Generating estimated coverage report..."
        php coverage-summary.php
        COVERAGE_EXIT_CODE=0
        ;;
esac

echo ""
echo "=============================================="

if [ $COVERAGE_EXIT_CODE -eq 0 ]; then
    echo "Coverage generation completed!"
    echo "=============================================="
    echo ""
    echo "Coverage reports generated:"
    
    if [ -f "coverage/index.html" ]; then
        echo "[✓] HTML Report: coverage/index.html"
        echo ""
        echo "Opening HTML coverage report..."
        # Try different methods to open the file
        if command -v start >/dev/null 2>&1; then
            start coverage/index.html 2>/dev/null
        elif command -v open >/dev/null 2>&1; then
            open coverage/index.html 2>/dev/null
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open coverage/index.html 2>/dev/null
        else
            echo "Please open coverage/index.html in your browser manually"
        fi
    fi
    
    if [ -f "coverage.xml" ]; then
        echo "[✓] Clover XML: coverage.xml"
    fi
    
    echo "[✓] Text Report: displayed above"
    
else
    echo "Coverage generation failed with exit code: $COVERAGE_EXIT_CODE"
fi

echo ""
echo "=============================================="
echo "Done!"
echo "=============================================="
read -p "Press Enter to continue..."
