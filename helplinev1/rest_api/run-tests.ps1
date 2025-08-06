# PHPUnit Test Runner for Windows PowerShell
# Execute PHPUnit tests with multiple output formats

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "PHPUnit Test Suite for REST API Application" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Set location to script directory
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "Current Directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Function to run command and measure time
function Run-TestCommand {
    param($Description, $Command)
    
    Write-Host "[$Description]" -ForegroundColor Green
    Write-Host "Running: $Command" -ForegroundColor Gray
    Write-Host ""
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-Expression $Command
    $stopwatch.Stop()
    
    Write-Host ""
    Write-Host "Completed in: $($stopwatch.Elapsed.TotalSeconds) seconds" -ForegroundColor Magenta
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host ""
}

# Test execution options
Write-Host "Select test execution mode:" -ForegroundColor Yellow
Write-Host "1. Quick test run (basic output)" -ForegroundColor White
Write-Host "2. Detailed test run (with descriptions)" -ForegroundColor White  
Write-Host "3. Coverage attempt (requires Xdebug/PCOV)" -ForegroundColor White
Write-Host "4. All tests + summary report" -ForegroundColor White
Write-Host "5. Individual test suites" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Run-TestCommand "Quick Test Run" "vendor\bin\phpunit --no-coverage"
    }
    "2" { 
        Run-TestCommand "Detailed Test Run" "vendor\bin\phpunit --testdox --colors=never"
    }
    "3" {
        Write-Host "Attempting coverage generation..." -ForegroundColor Yellow
        Write-Host "Note: This requires Xdebug or PCOV extension" -ForegroundColor Yellow
        Run-TestCommand "Coverage Generation" "phpdbg -qrr vendor\bin\phpunit --coverage-html coverage --coverage-text"
    }
    "4" {
        Run-TestCommand "Complete Test Suite" "vendor\bin\phpunit --testdox --colors=never"
        Run-TestCommand "Test Summary Report" "php test-execution-summary.php"
        Run-TestCommand "Coverage Summary" "php coverage-summary.php"
    }
    "5" {
        Write-Host "Available test suites:" -ForegroundColor Yellow
        Write-Host "- BasicTest" -ForegroundColor White
        Write-Host "- DatabaseTest" -ForegroundColor White
        Write-Host "- RestTest" -ForegroundColor White
        Write-Host "- IndexTest" -ForegroundColor White
        Write-Host "- ModelTest" -ForegroundColor White
        Write-Host "- ApiUtilsTest" -ForegroundColor White
        Write-Host "- SessionManagerTest" -ForegroundColor White
        Write-Host ""
        $suite = Read-Host "Enter test suite name (e.g., BasicTest)"
        Run-TestCommand "Individual Test Suite: $suite" "vendor\bin\phpunit --filter $suite --testdox"
    }
    default {
        Write-Host "Invalid choice. Running default test suite..." -ForegroundColor Red
        Run-TestCommand "Default Test Run" "vendor\bin\phpunit --testdox --colors=never"
    }
}

Write-Host "Test execution completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
