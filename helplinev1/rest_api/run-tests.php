<?php

/**
 * Simple test runner without coverage (works without XDebug)
 */

echo "🚀 Starting Helpline REST API Tests (Simple Mode)...\n\n";

// Check if composer is installed
if (!file_exists('vendor/autoload.php')) {
    echo "❌ Composer dependencies not found. Please run:\n";
    echo "   composer install\n\n";
    exit(1);
}

// Check if PHPUnit is available
$phpunitPaths = [
    'vendor/bin/phpunit',
    'vendor/phpunit/phpunit/phpunit'
];

$phpunitPath = null;
foreach ($phpunitPaths as $path) {
    if (file_exists($path)) {
        $phpunitPath = $path;
        break;
    }
}

if (!$phpunitPath) {
    echo "❌ PHPUnit not found. Please run:\n";
    echo "   composer install\n\n";
    exit(1);
}

echo "✅ Dependencies found. Running tests...\n\n";

// Run PHPUnit tests without coverage
$command = "php $phpunitPath --configuration phpunit.xml --verbose --colors=always";

echo "Command: $command\n";
echo str_repeat('-', 60) . "\n";

// Execute tests
passthru($command, $returnCode);

echo str_repeat('-', 60) . "\n";

if ($returnCode === 0) {
    echo "✅ Tests completed successfully!\n";
    echo "\n📊 Note: Code coverage disabled (requires XDebug extension)\n";
    echo "To enable coverage reporting:\n";
    echo "1. Install XDebug extension for PHP\n";
    echo "2. Use: php $phpunitPath --coverage-html coverage-html\n";
} else {
    echo "❌ Tests failed with return code: $returnCode\n";
    echo "Please check the output above for details.\n";
}

echo "\n";
echo "📚 Next steps:\n";
echo "1. Review test results above\n";
echo "2. Fix any failing tests\n";
echo "3. Add more tests for better coverage\n";
echo "4. Install XDebug to enable coverage reporting\n";
echo "\n";

exit($returnCode);