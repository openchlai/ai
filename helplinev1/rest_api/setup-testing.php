<?php

/**
 * Setup script for Helpline REST API Testing
 * This script helps you set up the testing environment
 */

echo "🔧 Setting up Helpline REST API Testing Environment...\n\n";

// Check PHP version
if (version_compare(PHP_VERSION, '7.4.0') < 0) {
    echo "❌ PHP 7.4 or higher is required. Current version: " . PHP_VERSION . "\n";
    echo "   Please upgrade your PHP installation.\n\n";
    exit(1);
}

echo "✅ PHP version: " . PHP_VERSION . " (compatible)\n";

// Check if composer.json exists
if (!file_exists('composer.json')) {
    echo "📝 Creating composer.json...\n";
    
    $composerConfig = [
        'require-dev' => [
            'phpunit/phpunit' => '^9.5'
        ],
        'autoload-dev' => [
            'psr-4' => [
                'Tests\\' => 'tests/'
            ]
        ]
    ];
    
    file_put_contents('composer.json', json_encode($composerConfig, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
    echo "✅ Created composer.json\n";
} else {
    echo "✅ Found existing composer.json\n";
}

// Check if composer is installed
$composerCommand = 'composer';
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $composerCommand = 'composer.bat';
}

$composerCheck = shell_exec("which $composerCommand 2>/dev/null");
if (empty($composerCheck)) {
    echo "❌ Composer not found. Please install Composer first:\n";
    echo "   curl -sS https://getcomposer.org/installer | php\n";
    echo "   sudo mv composer.phar /usr/local/bin/composer\n\n";
    echo "   Or on Windows, download from: https://getcomposer.org/\n\n";
    exit(1);
}

echo "✅ Composer is available\n";

// Create directory structure
$directories = [
    'tests',
    'tests/Unit',
    'tests/Integration',
    'test_data',
    'test_data/files',
    'test_data/calls'
];

foreach ($directories as $dir) {
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
        echo "📁 Created directory: $dir\n";
    } else {
        echo "✅ Directory exists: $dir\n";
    }
}

// Install composer dependencies
echo "\n📦 Installing testing dependencies...\n";
echo "Running: composer install\n";

$output = [];
$returnCode = 0;
exec('composer install 2>&1', $output, $returnCode);

if ($returnCode === 0) {
    echo "✅ Dependencies installed successfully\n";
} else {
    echo "❌ Failed to install dependencies:\n";
    foreach ($output as $line) {
        echo "   $line\n";
    }
    echo "\nTry running manually: composer install\n\n";
    exit(1);
}

// Verify PHPUnit installation
if (!file_exists('vendor/bin/phpunit')) {
    echo "❌ PHPUnit not found after installation\n";
    echo "   Try running: composer require --dev phpunit/phpunit\n\n";
    exit(1);
}

echo "✅ PHPUnit installed successfully\n";

// Check file permissions
$testFiles = ['tests', 'test_data'];
foreach ($testFiles as $file) {
    if (!is_writable($file)) {
        echo "⚠️  Warning: $file directory is not writable\n";
        echo "   You may need to run: chmod -R 755 $file\n";
    }
}

// Create .gitignore if it doesn't exist
if (!file_exists('.gitignore')) {
    $gitignore = "# Testing files\n";
    $gitignore .= "vendor/\n";
    $gitignore .= "coverage-html/\n";
    $gitignore .= "coverage.xml\n";
    $gitignore .= "coverage.txt\n";
    $gitignore .= "test-results.xml\n";
    $gitignore .= ".phpunit.result.cache\n";
    $gitignore .= "test_data/\n";
    
    file_put_contents('.gitignore', $gitignore);
    echo "📝 Created .gitignore file\n";
}

// Run a quick test to verify everything works
echo "\n🧪 Running test verification...\n";

$testOutput = [];
$testReturnCode = 0;
exec('vendor/bin/phpunit --version 2>&1', $testOutput, $testReturnCode);

if ($testReturnCode === 0) {
    echo "✅ PHPUnit is working: " . implode(' ', $testOutput) . "\n";
} else {
    echo "❌ PHPUnit test failed:\n";
    foreach ($testOutput as $line) {
        echo "   $line\n";
    }
}

// Final instructions
echo "\n🎉 Setup completed successfully!\n\n";
echo "📋 Next steps:\n";
echo "1. Run tests: php run-tests.php\n";
echo "2. Or run PHPUnit directly: ./vendor/bin/phpunit\n";
echo "3. View coverage report: open coverage-html/index.html\n";
echo "4. Read the testing guide: README-Testing.md\n\n";

echo "🎯 Your goal: Achieve 40% code coverage\n";
echo "📊 Current test files created:\n";
echo "   - tests/Unit/ModelTest.php (tests model definitions)\n";
echo "   - tests/Unit/RestTest.php (tests REST functions)\n";
echo "   - tests/Unit/SessionTest.php (tests session management)\n";
echo "   - tests/Unit/IndexTest.php (tests API endpoints)\n";
echo "   - tests/Integration/ApiIntegrationTest.php (integration tests)\n\n";

echo "💡 Tips:\n";
echo "   - Focus on testing business logic functions\n";
echo "   - Test both success and error scenarios\n";
echo "   - Add more tests if coverage is below 40%\n";
echo "   - Check the HTML coverage report to see what needs testing\n\n";

echo "Happy testing! 🚀\n";