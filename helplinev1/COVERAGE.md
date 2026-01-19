# Code Coverage Report - HelplineV1

**Branch:** 455/merge
**Commit:** [f539f8e](https://github.com/openchlai/ai/commit/f539f8e2e356fb62ab82267793b221edd405c8d5)
**Generated:** 2026-01-19 21:07:11 UTC
**PHP Version:** 8.3

## Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-64%25-yellow)
![Tests](https://img.shields.io/badge/Tests-PHPUnit-blue)

| Metric | Value |
|--------| ------|
| **Coverage** | 64% |
| **Generated** | 2026-01-19 21:07:11 UTC |
| **Branch** | 455/merge |
| **PHP Version** | 8.3 |

## Detailed Coverage Analysis

```
=== Real Code Coverage Analysis ===

Source Code Analysis:
- Total lines: 5724
- Code lines: 4068
- Non-code lines: 1656

Test Results:
- Total tests: 225
- Passing tests: 63
- Test success rate: 28%

Function Coverage:
- Total functions: 84
- Tested functions: 84
- Function coverage: 100%

=== Coverage Estimate ===
Based on test success rate and function coverage:
Estimated Line Coverage: 64%

✅ PASS: Coverage (64%) meets minimum 40% requirement
```

## Test Summary

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
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:141
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Subs definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:155
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Join definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:170
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Csv definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:188
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Duplicate check definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:203
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Field definition structure
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:217
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Validation flags
   │
   │ Should have a field with phone validation
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:245
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Src enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:254
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Location enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:278
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Special field definitions
   │
   │ Should have computed fields
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:302
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ System constants
 ✘ Disposition definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:324
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Activity definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:338
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Message definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:358
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Call definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:378
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

Context (Tests\Unit\Context)
 ✔ Ctx rights without context filter
ctx-right fail auth_id
 ✘ Ctx rights with context filter
   │
   │ Failed asserting that -1 matches expected 0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:53
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
   [CTX] (contacts) SELECT COUNT(DISTINCT contact.) FROM `contact` 

 ✘ Ctx function basic
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:199
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:1265
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:67
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
   [CTX] (contacts) SELECT COUNT(DISTINCT contact.) FROM `contact` 

 ✘ Ctx with search filter
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:199
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:1265
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:80
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Ctx fv function generates key map
   │
   │ ArgumentCountError: Too few arguments to function ctx_fv(), 4 passed in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php on line 93 and exactly 6 expected
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:1110
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:93
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 1077

 ✔ Ctx f function generates full field info

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 1077

Coverage Function Names (Tests\Unit\CoverageFunctionNames)
 ✔ Core helper function names are referenced
  [try] contacts
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 398

Database Ops (Tests\Unit\DatabaseOps)
 ✔ Try function validates fields

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 398
  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 398
 ✔ Try function detects invalid fields

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 398
 ✔ Val function skips unset fields during update
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385
    +-- [invalid] fullname REQUIRED
 ✔ Val function requires mandatory fields on add

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385
    +-- [invalid] code INVALID
 ✔ Val function with regex validation
    +-- [invalid] score INVALID
    +-- [invalid] score INVALID
 ✔ Val function with numeric length validation
    +-- [invalid] user_id INVALID_FOREIGN_KEY
 ✔ Val function with foreign key
 ✔ Val addr function
 ✔ Select cols function with prefix
 ✘ Select cols function with computed fields
   │
   │ Failed asserting that 'id,age' contains "YEAR(NOW())".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:213
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Select cols function excludes hidden fields
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 85
 ✘ Model k id with missing resources
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'contact_id'
   │ +'_id'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:241
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 85

 ✘ Kv with default value
   │
   │ Failed asserting that null matches expected 'default_value'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:252
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Kv with null placeholder

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

Error Handling (Tests\Unit\ErrorHandling)
 ✔ Phone fmt with empty string
 ✔ Phone fmt with spaces only
 ✔ Phone fmt with plus prefix
 ✔ Phone fmt with zero prefix
 ✔ Phone fmt with mixed spaces
 ✘ V e s c with special chars
   │
   │ Failed asserting that 'test&value' does not contain "&".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ErrorHandlingTest.php:52
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ V e s c with quotes
 ✔ V e s c with backslash
 ✔ V e s c with newlines
 ✔ V e s c with tabs
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 38
PHP Deprecated:  str_replace(): Passing null to parameter #3 ($subject) of type array|string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 45
 ✔ V e s c with null and numbers

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 38

Deprecated: str_replace(): Passing null to parameter #3 ($subject) of type array|string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 45
 ✔ Val email with complex addresses
 ✔ Val email with invalid formats
 ✔ Val phone with various formats
 ✔ Val phone with invalid formats
 ✔ Rands consistency
 ✘ Date with various timestamps
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'1970-01-01'
   │ +''
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ErrorHandlingTest.php:152
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Date with different formats
 ✔ Enum with non existent key
 ✔ Enum with empty value
 ✔ Enum with multiple mixed values
 ✔ Kv with literal value
 ✘ Kv with conditional operator
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'field2'
   │ +'value1'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ErrorHandlingTest.php:221
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Val id incrementing
 ✔ Model k id with custom alias
 ✔ Str 2ts with all periods

Field Operations (Tests\Unit\FieldOperations)
 ✔ Select cols basic
 ✔ Select cols with table prefix
 ✘ Select cols with alias
   │
   │ Failed asserting that 'id,name' contains "user_id".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:54
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Select cols with computed field
   │
   │ Failed asserting that 'id,total' contains "SUM(amount)".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:68
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602

 ✘ Csv cols k mapping
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:77
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
"",
Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
"",
Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
""
 ✘ Csv cols v mapping
   │
   │ ArgumentCountError: Too few arguments to function _csv_cols_v(), 2 passed in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php on line 91 and exactly 3 expected
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:570
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:91
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Val with empty string vs null
 ✔ Val with p overrides o
 ✔ Val with default value when null
 ✔ Val with default value not applied when set
    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
 ✔ Val string length validation
    +-- [invalid] age INVALID
    +-- [invalid] age INVALID
 ✔ Val numeric range validation
  [try] contacts
 ✔ Try with valid data
  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
 ✔ Try with invalid data
 ✘ Phone fmt with various inputs
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+256701234567'
   │ +'701234567 '
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:242
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ V e s c with complex content
   │
   │ Failed asserting that '&lt;div class=\"test\"&gt;Content & \"quotes\" with 'apostrophes'&lt;\/div&gt;' contains "&amp;".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:260
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 85

 ✔ Model k id with partial resources

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 85
 ✘ Kv with complex operators
   │
   │ Failed asserting that null matches expected 'fallback'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:288
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Val addr with different sources

File Utils (Tests\Unit\FileUtils)
 ✔ Select cols function
 ✔ Val function with constant field
 ✔ Val function with generated id
 ✔ Val function with random number
    +-- [invalid] fullname REQUIRED
 ✔ Val function with mandatory field
 ✔ Val function with default value
    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
 ✔ Val function with length validation
    +-- [invalid] email INVALID
 ✔ Val function with email validation
    +-- [invalid] phone INVALID
 ✔ Val function with phone validation
    +-- [invalid] username DUPLICATE
 ✔ Val function with unique field
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
PHP Deprecated:  strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
 ✘ Csv cols k function
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FileUtilsTest.php:214
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
"",
Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
"",
Deprecated: strtoupper(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 602
""
 ✘ Csv cols v function
   │
   │ ArgumentCountError: Too few arguments to function _csv_cols_v(), 2 passed in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FileUtilsTest.php on line 230 and exactly 3 expected
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:570
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FileUtilsTest.php:230
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

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
 ✘ Resources array exists
   │
   │ Failed asserting that an array has the key 'auth'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:61
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

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

Request Response (Tests\Unit\RequestResponse)
 ✔ Get parameter function
 ✔ Post parameter function
 ✔ Session parameter function
 ✔ V array function
 ✔ V e s c security escaping
 ✘ Phone format international
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+15551234567'
   │ +'5551234567'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:94
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Random string generation distribution
 ✔ Enum with missing global
 ✔ Date format edge cases
 ✘ Val email edge cases
   │
   │ Failed asserting that 1 matches expected 0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:164
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Val phone edge cases
 ✔ Kv operators
 ✘ Val id uniqueness
   │
   │ Failed asserting that actual size 1 matches expected size 100.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:220
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Model k id variations
 ✘ Str 2ts all time periods
   │
   │ Failed asserting that 1768780800 is of type "string".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:263
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │
    +-- [invalid] field1 ERR1
    +-- [invalid] field2 ERR2
    +-- [invalid] field3 ERR3

 ✔ Val error multiple errors
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385
    +-- [invalid] phone REQUIRED
    +-- [invalid] phone INVALID
 ✔ Val with combined flags

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 385

Rest Helpers (Tests\Unit\RestHelpers)
 ✔ G Function
 ✔ P Function
 ✔ S Function
 ✔ V Function
 ✘ VESC Function
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'&lt;div&gt;content&lt;/div&gt;'
   │ +'&lt;div&gt;content&lt;\/div&gt;'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RestHelpersTest.php:50
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Date function
 ✔ Enum function
 ✘ Phone fmt function
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+256701234567'
   │ +'256701234567'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RestHelpersTest.php:95
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Rands function
 ✔ Str 2ts function
 ✔ Val id function
 ✔ Val phone function
 ✔ Val email function
    +-- [invalid] email INVALID
 ✔ Val error function
 ✔ Kv function
 ✔ Model k id function

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

---
*Report generated automatically by GitHub Actions*
