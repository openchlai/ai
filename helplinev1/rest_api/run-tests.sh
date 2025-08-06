#!/bin/bash
# PHPUnit Test Runner for Git Bash
# Run PHPUnit tests with multiple output formats

echo "=============================================="
echo "PHPUnit Test Suite for REST API Application"
echo "=============================================="

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo "Current Directory: $(pwd)"
echo ""

# Function to run command with timing
run_test_command() {
    local description="$1"
    local command="$2"
    
    echo "[$description]"
    echo "Running: $command"
    echo ""
    
    start_time=$(date +%s)
    eval "$command"
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "Completed in: ${duration} seconds"
    echo "=============================================="
    echo ""
}

# Check if vendor directory exists
if [ ! -d "vendor" ]; then
    echo "❌ Error: vendor directory not found!"
    echo "Please run 'composer install' first."
    exit 1
fi

# Menu for test execution
echo "Select test execution mode:"
echo "1. Quick test run (basic output)"
echo "2. Detailed test run (with descriptions)"
echo "3. Coverage attempt (requires coverage driver)"
echo "4. All tests + summary report"
echo "5. Individual test suites"
echo "6. Run specific test file"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        run_test_command "Quick Test Run" "vendor/bin/phpunit --no-coverage"
        ;;
    2)
        run_test_command "Detailed Test Run" "vendor/bin/phpunit --testdox --colors=never"
        ;;
    3)
        echo "Attempting coverage generation..."
        echo "Note: This requires Xdebug, PCOV, or phpdbg"
        if command -v phpdbg >/dev/null 2>&1; then
            run_test_command "Coverage with phpdbg" "phpdbg -qrr vendor/bin/phpunit --coverage-html coverage --coverage-text"
        else
            run_test_command "Coverage attempt" "vendor/bin/phpunit --coverage-html coverage --coverage-text"
        fi
        
        # Open coverage report if generated
        if [ -f "coverage/index.html" ]; then
            echo "Opening coverage report in browser..."
            start coverage/index.html 2>/dev/null || open coverage/index.html 2>/dev/null || echo "Coverage report saved to: coverage/index.html"
        fi
        ;;
    4)
        run_test_command "Complete Test Suite" "vendor/bin/phpunit --testdox --colors=never"
        run_test_command "Test Summary Report" "php test-execution-summary.php"
        run_test_command "Coverage Summary" "php coverage-summary.php"
        ;;
    5)
        echo "Available test suites:"
        echo "- BasicTest"
        echo "- DatabaseTest"
        echo "- RestTest"
        echo "- IndexTest"
        echo "- ModelTest"
        echo "- ApiUtilsTest"
        echo "- SessionManagerTest"
        echo "- ValidationTest"
        echo ""
        read -p "Enter test suite name (e.g., BasicTest): " suite
        run_test_command "Individual Test Suite: $suite" "vendor/bin/phpunit --filter $suite --testdox"
        ;;
    6)
        echo "Available test files:"
        ls -1 tests/Unit/*.php | sed 's/tests\/Unit\///' | sed 's/\.php$//'
        echo ""
        read -p "Enter test file name (without .php): " testfile
        run_test_command "Test File: $testfile" "vendor/bin/phpunit tests/Unit/${testfile}.php --testdox"
        ;;
    *)
        echo "Invalid choice. Running default test suite..."
        run_test_command "Default Test Run" "vendor/bin/phpunit --testdox --colors=never"
        ;;
esac

echo "Test execution completed!"
read -p "Press Enter to exit..."
