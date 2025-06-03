# Testing Guide for index.php

This guide walks you through testing the PHP REST API defined in `index.php` using a comprehensive test suite.

## Quick Start

1. **Run all tests:**
   ```bash
   php run-index-tests.php
   ```

2. **Run with coverage:**
   ```bash
   php run-index-tests.php --coverage
   ```

3. **Run specific test:**
   ```bash
   php run-index-tests.php --filter=testMuuFunction
   ```

## File Structure

```
api/
├── index.php                    # Main API file to test
├── bootstrap.php                # Test bootstrap and mocks
├── phpunit.xml                  # PHPUnit configuration
├── run-index-tests.php          # Simple test runner
├── tests/
│   ├── IndexTest.php            # Complete test suite for index.php
│   └── helpers/
│       └── TestHelpers.php      # Test utilities
└── coverage-html/               # Coverage reports (generated)
```

## What Gets Tested

The `IndexTest.php` file provides comprehensive coverage for all functions in `index.php`:

### Core Functions
- ✅ `copy_from_pabx()` - Audio file retrieval from archive
- ✅ `muu()` - Integration with voiceapps system  
- ✅ `notify()` & `_notify_()` - Notification system
- ✅ `message_out()` & `_message_in()` - Message handling

### Voice Integration Functions
- ✅ `_sup()` - Supervisor actions (spy, whisper, barge)
- ✅ `_chan()` - Channel management (invite, dial, transfer, hangup)
- ✅ `_agent()` - Agent actions (login, logout, auto-answer)

### Dashboard Functions
- ✅ `_wallonly()` - Wallboard metrics and statistics
- ✅ `_dash()` - Dashboard data aggregation
- ✅ `_home()` - Application initialization

### Request Handling
- ✅ `_request_()` - Main entry point and routing
- ✅ HTTP method handling (GET/POST)
- ✅ Authentication and authorization
- ✅ Error responses

### Integration Workflows
- ✅ Complete message → case → escalation workflows
- ✅ Agent login → call handling → case creation
- ✅ Multi-channel communication
- ✅ Error handling scenarios

## Test Categories

You can run specific categories of tests using the `--filter` option:

```bash
# Test specific function groups
php run-index-tests.php --filter=Muu           # muu() function tests
php run-index-tests.php --filter=Agent         # _agent() function tests
php run-index-tests.php --filter=Chan          # _chan() function tests
php run-index-tests.php --filter=Sup           # _sup() function tests
php run-index-tests.php --filter=Dash          # _dash() function tests
php run-index-tests.php --filter=Wallonly      # _wallonly() function tests
php run-index-tests.php --filter=Message       # Message handling tests
php run-index-tests.php --filter=Workflow      # End-to-end workflow tests
php run-index-tests.php --filter=Request       # _request_() function tests
```

## Understanding Test Output

### Successful Test Run
```
=== Index.php Test Runner ===
✓ All tests passed successfully!

What was tested:
  ✓ Core functions (copy_from_pabx, muu, notify)
  ✓ Message handling (_message_in, message_out)  
  ✓ Voice integration (_sup, _chan, _agent)
  ✓ Dashboard functions (_wallonly, _dash, _home)
  ✓ Request routing (_request_)
  ✓ Integration workflows
  ✓ Error handling scenarios
```

### Test with Coverage
When you run with `--coverage`, you'll get:
- HTML coverage report in `coverage-html/index.html`
- Text coverage summary in the terminal
- Line-by-line coverage analysis

### Verbose Output
Use `--verbose` to see detailed information about each test:
```bash
php run-index-tests.php --verbose
```

## Mock Framework

The test suite uses a comprehensive mocking system in `bootstrap.php`:

### What's Mocked
- **Database connections**: MySQL queries and results
- **HTTP requests**: cURL operations to external services
- **Session management**: PHP session handling
- **File operations**: Audio file downloads
- **External services**: Gateway APIs, voiceapps integration

### Mock Data
Test helpers provide realistic mock data for:
- SMS/WhatsApp messages
- Case records  
- Agent actions
- Channel operations
- Dashboard metrics

## Common Test Scenarios

### Testing Message Flow
```php
// Incoming message → Case creation → Response
testCompleteWorkflow()
```

### Testing Agent Operations  
```php
// Agent login → Call handling → Case creation
testAgentWorkflow()
```

### Testing Error Handling
```php
// Invalid roles, bad extensions, unauthorized access
testErrorHandling()
```

### Testing Multi-Channel Communication
```php
// SMS, WhatsApp, Email processing
testMultiChannelCommunication()
```

## Troubleshooting

### Common Issues

1. **Headers already sent error**
   - Check that `header()` function is properly mocked in bootstrap
   - Ensure no output before headers in test setup

2. **Database connection failed**
   - Verify mock database functions are loaded
   - Check database constants in bootstrap

3. **Session errors**
   - Ensure `$_SESSION` variables are properly initialized
   - Check session mocking setup

4. **Function not found**
   - Verify all required files are included
   - Check that mock functions are defined

### Debug Tips

1. **Run single test:**
   ```bash
   php run-index-tests.php --filter=testSpecificFunction --verbose
   ```

2. **Check mock responses:**
   - Review `TestHelpers::createMockData()` 
   - Verify mock function behavior

3. **Inspect output:**
   - Check `tests/results/` directory for logs
   - Review coverage reports for missed code paths

## Extending Tests

### Adding New Test Cases

1. Add new test method to `IndexTest.php`:
   ```php
   public function testNewFunctionality() {
       // Test setup
       // Call function
       // Assert results
   }
   ```

2. Use existing helpers:
   ```php
   TestHelpers::setServerVars('POST', '/endpoint');
   TestHelpers::setPostData($data);
   $result = TestHelpers::captureOutput(function() {
       return _request_();
   });
   ```

### Creating Mock Data

Use `TestHelpers::createMockData()` for consistent test data:
```php
$messageData = TestHelpers::createMockData('message');
$caseData = TestHelpers::createMockData('case');
$agentData = TestHelpers::createMockData('agent_action');
```

## Best Practices

1. **Keep tests independent** - Each test should reset state
2. **Use descriptive names** - Test method names should explain what's being tested
3. **Test error conditions** - Include negative test cases
4. **Mock external calls** - Never make real HTTP requests or database calls
5. **Verify responses** - Check both return codes and output content

## Integration with CI/CD

The test suite is designed for automation:

```bash
# In your CI pipeline
php run-index-tests.php --coverage
```

Exit codes:
- `0` = All tests passed
- `Non-zero` = Tests failed

## Performance

The complete test suite typically runs in under 30 seconds and includes:
- 50+ individual test methods
- 200+ assertions
- Full function coverage
- Integration scenarios
- Error handling tests

## Getting Help

If tests fail:

1. Check the verbose output for specific error messages
2. Review the mock setup in `bootstrap.php`
3. Verify that `index.php` functions match expected signatures
4. Check the `tests/results/` directory for detailed logs

The test suite provides confidence that your REST API functions correctly across all supported scenarios and use cases.