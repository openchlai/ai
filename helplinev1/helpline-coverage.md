# 📊 HelplineV1 Code Coverage Report

**Branch:** justphyl
**Commit:** `8c6834a`
**Generated:** 2025-08-15 01:41:05 UTC
**PHP Version:** 8.3
**Workflow:** [`16980813654`](https://github.com/openchlai/ai/actions/runs/16980813654)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-59%25-orange)
![Tests](https://img.shields.io/badge/Tests-PHPUnit-blue)

| Metric | Value | Status |
|--------|-------|--------|
| **Overall Coverage** | **59%** | 🟠 Fair |
| **Generated** | 2025-08-15 01:41:05 UTC | |
| **Branch** | justphyl | |
| **PHP Version** | 8.3 | |

## 📈 Detailed Coverage Analysis

```
=== Real Code Coverage Analysis ===

Source Code Analysis:
- Total lines: 5724
- Code lines: 4068
- Non-code lines: 1656

Test Results:
- Total tests: 114
- Passing tests: 63
- Test success rate: 55%

Function Coverage:
- Total functions: 84
- Tested functions: 53
- Function coverage: 63.1%

=== Coverage Estimate ===
Based on test success rate and function coverage:
Estimated Line Coverage: 59%

✅ PASS: Coverage (59%) meets minimum 40% requirement
```

## 🧪 Test Summary

| Test Class | Test Method | Status |\n|------------|-------------|--------|\n| PHPUnit | Test Execution | ✅ Completed |\n

### Raw Test Output

```
PHPUnit 9.6.23 by Sebastian Bergmann and contributors.

Api Utils (Tests\Unit\ApiUtils)
 ✔ Resource definitions
 ✔ Metrics definitions
 ↩ Rights system structure
 ↩ Enum definitions
 ✘ Api definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:139
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Subs definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:153
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Join definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:168
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Csv definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:186
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Duplicate check definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:201
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Field definition structure
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:215
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Validation flags
   │
   │ Should have a field with phone validation
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:243
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Src enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:252
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Location enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:276
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Special field definitions
   │
   │ Should have computed fields
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:300
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ System constants
 ✘ Disposition definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:322
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Activity definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:336
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Message definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:356
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Call definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:376
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Basic (Tests\Unit\Basic)
 ✔ Php version
 ✔ Basic assertion
 ✔ Model file exists
 ✔ Rest file exists
 ✔ Can include model file
 ✘ Global variables exist
   │
   │ $RIGHTS_1 should be defined
   │ Failed asserting that an array has the key 'RIGHTS_1'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/BasicTest.php:49
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Rest functions exist
 ✔ Utility functions
 ✔ Validation functions

Database (Tests\Unit\Database)
 ✔ Select cols function
    +-- [invalid] email INVALID
 ✔ Validation error handling
    +-- [invalid] email INVALID
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385
    +-- [invalid] required_field REQUIRED
 ✔ Field validation

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385
 ✔ Constant and generated values
 ✔ Default values
 ✔ Update field handling
 ✘ Duplicate field validation
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseTest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Custom field mapping
 ✔ Priority handling
 ✔ V global function
 ✔ Global get post session
 ☢ Select query building
 ✔ Empty field handling

Index (Tests\Unit\Index)
 ✔ Copy from pabx Function
 ✔ Muu Function
 ✔ Message out Function
 ✔ National registry Function
 ✘ Message in Function
   │
   │ Failed asserting that '' contains "success".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php:321
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Sup Function
 ✘ Chan Function
   │
   │ Failed asserting that 202 matches expected 413.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php:433
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Model (Tests\Unit\Model)
 ✔ Resources array exists
 ✘ Rights array exists
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:69
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Auth definition structure
 ✔ Contacts definition structure
 ✘ Enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:107
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Api definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:131
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Subs definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:146
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Join definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:161
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Csv definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:179
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Duplicate check definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:195
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Metrics definitions

Rest (Tests\Unit\Rest)
 ✔ Global helper functions
 ✔ Vesc function
 ✔ Date function
 ✔ Enum function
 ✔ Model k id function
 ✔ Validation functions
 ✔ Random string generation
 ✔ Timestamp conversion
    +-- [invalid] test_field INVALID
 ✔ Error handling
 ✔ Id generation
 ✔ Query building
,contacts |2 | 0
 ✘ Uri parsing
   │
   │ Failed asserting that 404 matches expected 0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RestTest.php:241
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
rest_uri_response_error - 404
{ "errors":[["error","The requested URL \/ was not found on this server"]]}
```

## 📁 Generated Files

- `coverage.xml` - XML coverage report for CI/CD integration
- `coverage-html/` - HTML coverage report for detailed browsing
- `coverage-analysis.txt` - Detailed coverage analysis
- `test-summary.txt` - Test execution summary

## 🔍 How to View Coverage

### HTML Report (Recommended)
Open `helplinev1/rest_api/coverage-html/index.html` in your browser for an interactive view.

### Command Line
```bash
cd helplinev1/rest_api
./vendor/bin/phpunit --coverage-text
```

### XML Integration
Use `coverage.xml` for integration with code coverage services like Codecov.

## 📊 Coverage Trends

- **Current Coverage**: 59%
- **Target**: 80%+ (Excellent), 60%+ (Good), 40%+ (Minimum)
- **Framework**: PHPUnit with PCOV

---
*Report generated automatically by GitHub Actions*
*Access this report at: [helpline-coverage.md](https://github.com/openchlai/ai/blob/justphyl/helplinev1/helpline-coverage.md)*
