# Code Coverage Report - HelplineV1

**Branch:** 455/merge
**Commit:** [e0b0f82](https://github.com/openchlai/ai/commit/e0b0f8255381164dd2953b6ed1451336b6051a08)
**Generated:** 2026-01-19 21:52:38 UTC
**PHP Version:** 8.3

## Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-4%25-red)
![Tests](https://img.shields.io/badge/Tests-PHPUnit-blue)

| Metric | Value |
|--------| ------|
| **Coverage** | 4% |
| **Generated** | 2026-01-19 21:52:38 UTC |
| **Branch** | 455/merge |
| **PHP Version** | 8.3 |

## Detailed Coverage Analysis

```
=== Real Code Coverage Analysis ===

=== PHPUnit Raw Output (for debugging) ===
PHPUnit 9.6.23 by Sebastian Bergmann and contributors.

EF..ESSSSSS....FFFFFFF............FSSSS.FF  [try] contacts
.  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
..    +-- [invalid] fullname REQUIRED
.    +-- [invalid] code INVALID
.    +-- [invalid] score INVALID
    +-- [invalid] score INVALID
.    +-- [invalid] user_id INVALID_FOREIGN_KEY
......FR.    +-- [invalid] email INVALID
.    +-- [invalid] email INVALID
    +-- [invalid] required_field REQUIRED
.....  63 / 225 ( 28%)
....FFFSS........    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
.    +-- [invalid] age INVALID
    +-- [invalid] age INVALID
.  [try] contacts
.  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
...FF.....FF.........FFFF...........    +-- [invalid] field1 ERR1
    +-- [invalid] field2 ERR2
    +-- [invalid] field3 ERR3
.    +-- [invalid] phone REQUIRED
    +-- [invalid] phone INVALID
.FF... 126 / 225 ( 56%)
........    +-- [invalid] email INVALID
...FFF.......    +-- [invalid] test_field INVALID
...SS....    +-- [invalid] fullname REQUIRED
..    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
.    +-- [invalid] email INVALID
.    +-- [invalid] phone INVALID
.    +-- [invalid] username DUPLICATE
......F..................... 189 / 225 ( 84%)
.................    +-- [invalid] test_field INVALID
...contacts, |2 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
contacts,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
.
Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
rest_uri_response_error - 404
..PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
F
Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
F
Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
FScontacts,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
.
Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
nonexistent,123 |3 | 1
.contacts^search,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
.
Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
.    +-- [invalid] test_field TEST_ERROR
..rest_uri_response_error - 404
...                            225 / 225 (100%)

Time: 00:00.430, Memory: 28.00 MB

There were 2 errors:

1) Tests\Unit\SessionManagerTest::testSessionRead
TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given

/home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
/home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:115
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

2) Tests\Unit\SessionTest::testSs_read_Function
TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given

/home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
/home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionTest.php:93
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

--

There were 32 failures:

1) Tests\Unit\SessionManagerTest::testSessionIdExtraction
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'test_session_123'
+'g3ch7dohnhn4ov7ghtcqapsg7d'

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:92
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

2) Tests\Unit\ApiUtilsTest::testApiDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:142
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

3) Tests\Unit\ApiUtilsTest::testSubsDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:155
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

4) Tests\Unit\ApiUtilsTest::testCsvDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:188
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

5) Tests\Unit\ApiUtilsTest::testDuplicateCheckDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:203
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

6) Tests\Unit\ApiUtilsTest::testSrcEnumDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:255
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

7) Tests\Unit\ApiUtilsTest::testLocationEnumDefinitions
Failed asserting that null is of type "array".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:278
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

8) Tests\Unit\ApiUtilsTest::testValidationFlags
Should have a field with email validation
Failed asserting that null is not null.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:246
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

9) Tests\Unit\ContextTest::testCtxFvFunctionGeneratesKeyMap
Failed asserting that '' contains "id".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:71
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

10) Tests\Unit\DatabaseOpsTest::testSelectColsFunctionWithComputedFields
Failed asserting that 'id,age' contains "YEAR(NOW())".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:213
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

11) Tests\Unit\DatabaseOpsTest::testKvWithDefaultValue
Failed asserting that null matches expected 'default_value'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:252
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

12) Tests\Unit\DatabaseTest::testDuplicateFieldValidation
Failed asserting that 0 matches expected 1.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseTest.php:202
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

13) Tests\Unit\FieldOperationsTest::testPhoneFmtWithVariousInputs
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'+256701234567'
+'701234567 '

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:227
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

14) Tests\Unit\FieldOperationsTest::testVESCWithComplexContent
Failed asserting that '&lt;div class=\"test\"&gt;Content & \"quotes\" with 'apostrophes'&lt;\/div&gt;' contains "&amp;".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:245
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

15) Tests\Unit\FieldOperationsTest::testKvWithComplexOperators
Failed asserting that null matches expected 'fallback'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:273
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

16) Tests\Unit\IndexTest::test_message_in_Function
Failed asserting that '' contains "success".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php:321
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

17) Tests\Unit\IndexTest::test_chan_Function
Failed asserting that 202 matches expected 413.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php:433
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

18) Tests\Unit\ModelTest::testResourcesArrayExists
Failed asserting that an array has the key 'auth'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:61
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

19) Tests\Unit\ModelTest::testRightsArrayExists
Failed asserting that an array has the key 'auth'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:70
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

20) Tests\Unit\RequestResponseTest::testPhoneFormatInternational
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'+15551234567'
+'5551234567'

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:94
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

21) Tests\Unit\RequestResponseTest::testValEmailEdgeCases
Failed asserting that 1 matches expected 0.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:164
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

22) Tests\Unit\RequestResponseTest::testValIdUniqueness
Failed asserting that actual size 1 matches expected size 100.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:220
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

23) Tests\Unit\RequestResponseTest::testStr2tsAllTimePeriods
Failed asserting that 1768780800 is of type "string".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:263
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

24) Tests\Unit\RestHelpersTest::testVESC_Function
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'&lt;div&gt;content&lt;/div&gt;'
+'&lt;div&gt;content&lt;\/div&gt;'

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RestHelpersTest.php:50
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

25) Tests\Unit\RestHelpersTest::testPhoneFmtFunction
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'+256701234567'
+'256701234567'

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RestHelpersTest.php:95
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

26) Tests\Unit\ValidationTest::testPhoneValidation
Failed asserting that 0 matches expected 1.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:37
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

27) Tests\Unit\ValidationTest::testPhoneFormatting
Failed asserting that two strings are equal.
--- Expected
+++ Actual
@@ @@
-'+256701234567'
+'256701234567'

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:99
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

28) Tests\Unit\ValidationTest::testValidIdGeneration
Failed asserting that 17688595570920.0 is not equal to 17688595570920.0.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:245
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

29) Tests\Unit\BasicTest::testGlobalVariablesExist
Failed asserting that an array has the key 'contacts'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/BasicTest.php:57
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

30) Tests\Integration\ApiIntegrationTest::testValidationFlow
Failed asserting that null matches expected '+256701234567'.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:203
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

31) Tests\Integration\ApiIntegrationTest::testValidationErrors
Failed asserting that 0 matches expected 1.

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:226
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

32) Tests\Integration\ApiIntegrationTest::testContextFiltering
Failed asserting that '"id":["0","id","","ID",""],"fullname":["1","fullname","John","Full Name",""]' contains "contacts_k".

/home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:249
/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

--

There was 1 risky test:

1) Tests\Unit\DatabaseTest::testSelectQueryBuilding
This test is annotated with "@doesNotPerformAssertions" but performed 1 assertions

/home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122

ERRORS!
Tests: 225, Assertions: 1170, Errors: 2, Failures: 32, Skipped: 15, Risky: 1.

Generating code coverage report in Clover XML format ... PHP Fatal error:  Cannot redeclare copy_from_pabx() (previously declared in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php(114) : eval()'d code:2) in /home/runner/work/ai/ai/helplinev1/rest_api/api/index.php on line 17

Fatal error: Cannot redeclare copy_from_pabx() (previously declared in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php(114) : eval()'d code:2) in /home/runner/work/ai/ai/helplinev1/rest_api/api/index.php on line 17

=== End Raw Output ===

Parsed from summary format:
  Total: 225, Passing: 176, Errors: 2, Failures: 32, Skipped: 15

Source Code Analysis:
- Total lines: 5731
- Code lines: 4071
- Non-code lines: 1660

Test Results:
- Total tests: 225
- Passing tests: 176
- Test success rate: 78.2%

Function Coverage:
- Total functions: 84
- Tested functions: 84
- Function coverage: 100%

=== Coverage Estimate ===
Based on test success rate (78.2%) and function coverage (100%):
Estimated Line Coverage: 89.1%

Coverage Report Complete: 89.1%
```

## Test Summary

```
PHPUnit 9.6.23 by Sebastian Bergmann and contributors.

Api Utils (Tests\Unit\ApiUtils)
 ✔ Resource definitions
 ✔ Metrics definitions
 ✔ Rights system structure
 ✔ Enum definitions
 ✘ Api definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:142
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Subs definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:155
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Join definitions
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

 ✔ Field definition structure
 ✘ Validation flags
   │
   │ Should have a field with email validation
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:246
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Src enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:255
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Location enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:278
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Special field definitions
 ✔ System constants
 ✔ Disposition definitions
 ✔ Activity definitions
 ✔ Message definitions
 ✔ Call definitions

Basic (Tests\Unit\Basic)
 ✔ Php version
 ✔ Basic assertion
 ✔ Model file exists
 ✔ Rest file exists
 ✔ Can include model file
 ✔ Global variables exist
 ✔ Rest functions exist
 ✔ Utility functions
 ✔ Validation functions

Context (Tests\Unit\Context)
 ✔ Ctx rights without context filter
 ↩ Ctx rights with context filter
 ↩ Ctx function basic
 ↩ Ctx with search filter
 ✘ Ctx fv function generates key map
   │
   │ Failed asserting that '' contains "id".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:71
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ↩ Ctx f function generates full field info
  [try] contacts
  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
    +-- [invalid] fullname REQUIRED
    +-- [invalid] code INVALID
    +-- [invalid] score INVALID
    +-- [invalid] score INVALID
    +-- [invalid] user_id INVALID_FOREIGN_KEY
    +-- [invalid] email INVALID
    +-- [invalid] email INVALID
    +-- [invalid] required_field REQUIRED
    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
    +-- [invalid] age INVALID
    +-- [invalid] age INVALID
  [try] contacts
  [try] contacts
    +-- [invalid] fullname REQUIRED
    +-- [invalid] email INVALID
    +-- [invalid] field1 ERR1
    +-- [invalid] field2 ERR2
    +-- [invalid] field3 ERR3
    +-- [invalid] phone REQUIRED
    +-- [invalid] phone INVALID
    +-- [invalid] email INVALID
    +-- [invalid] test_field INVALID
    +-- [invalid] fullname REQUIRED
    +-- [invalid] code INVALID
    +-- [invalid] code INVALID
    +-- [invalid] email INVALID
    +-- [invalid] phone INVALID
    +-- [invalid] username DUPLICATE

Coverage Function Names (Tests\Unit\CoverageFunctionNames)
 ✔ Core helper function names are referenced

Database Ops (Tests\Unit\DatabaseOps)
 ✔ Try function validates fields
 ✔ Try function detects invalid fields
 ✔ Val function skips unset fields during update
 ✔ Val function requires mandatory fields on add
 ✔ Val function with regex validation
 ✔ Val function with numeric length validation
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
 ✔ Model k id with missing resources
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
 ✔ Validation error handling
 ✔ Field validation
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
 ✔ V e s c with special chars
 ✔ V e s c with quotes
 ✔ V e s c with backslash
 ✔ V e s c with newlines
 ✔ V e s c with tabs
 ✔ V e s c with null and numbers
 ✔ Val email with complex addresses
 ✔ Val email with invalid formats
 ✔ Val phone with various formats
 ✔ Val phone with invalid formats
 ✔ Rands consistency
 ✔ Date with various timestamps
 ✔ Date with different formats
 ✔ Enum with non existent key
 ✔ Enum with empty value
 ✔ Enum with multiple mixed values
 ✔ Kv with literal value
 ✔ Kv with conditional operator
 ✔ Val id incrementing
 ✔ Model k id with custom alias
 ✔ Str 2ts with all periods

Field Operations (Tests\Unit\FieldOperations)
 ✔ Select cols basic
 ✔ Select cols with table prefix
 ✔ Select cols with alias
 ✔ Select cols with computed field
 ↩ Csv cols k mapping
 ↩ Csv cols v mapping
 ✔ Val with empty string vs null
 ✔ Val with p overrides o
 ✔ Val with default value when null
 ✔ Val with default value not applied when set
 ✔ Val string length validation
 ✔ Val numeric range validation
 ✔ Try with valid data
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
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:227
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ V e s c with complex content
   │
   │ Failed asserting that '&lt;div class=\"test\"&gt;Content & \"quotes\" with 'apostrophes'&lt;\/div&gt;' contains "&amp;".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:245
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Model k id with partial resources
 ✘ Kv with complex operators
   │
   │ Failed asserting that null matches expected 'fallback'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:273
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Val addr with different sources

File Utils (Tests\Unit\FileUtils)
 ✔ Select cols function
 ✔ Val function with constant field
 ✔ Val function with generated id
 ✔ Val function with random number
 ✔ Val function with mandatory field
 ✔ Val function with default value
 ✔ Val function with length validation
 ✔ Val function with email validation
 ✔ Val function with phone validation
 ✔ Val function with unique field
 ↩ Csv cols k function
 ↩ Csv cols v function

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
   │ Failed asserting that an array has the key 'auth'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:70
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Auth definition structure
 ✔ Contacts definition structure
 ✔ Enum definitions
 ✔ Api definitions
 ✔ Subs definitions
 ✔ Join definitions
 ✔ Csv definitions
 ✔ Duplicate check definitions
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

 ✔ Val error multiple errors
 ✔ Val with combined flags

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
contacts, |2 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
contacts,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
 ✔ Uri parsing

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
rest_uri_response_error - 404
 ✔ Response error handling
 ✔ Value extraction function

Session Manager (Tests\Unit\SessionManager)
 ✘ Session id extraction
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'test_session_123'
   │ +'dqj3nkc2j5qgfe7d8fbohjbd9v'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:92
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Session open close
 ✘ Session read
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:115
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Session write

Session (Tests\Unit\Session)
 ✔ Ss id Function
 ✔ Ss open Function
 ✔ Ss close Function
 ✘ Ss read Function
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionTest.php:93
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Ss write Function
 ↩ Ss destroy Function
 ↩ Ss gc Function
 ↩ Ss new Function
 ↩ Ss new phone Function
 ↩ Ss Function
 ↩ Auth Function

Validation (Tests\Unit\Validation)
 ✘ Phone validation
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Email validation
 ✔ Address validation
 ✘ Phone formatting
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+256701234567'
   │ +'256701234567'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:99
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Random string generation
 ✔ Value escaping
 ✔ Date formatting
 ✔ Enum formatting
 ✔ Str 2 ts function
 ✔ Validation errors
 ✘ Valid id generation
   │
   │ Failed asserting that 17688595582045.0 is not equal to 17688595582045.0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:245
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✔ Kv function
 ✔ Model key id generation
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 376

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 388
contacts,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171

Api Integration (Tests\Integration\ApiIntegration)
 ✔ Rest uri parse get request
 ↩ Rest uri parse post request

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
nonexistent,123 |3 | 1
 ✔ Rest uri parse invalid resource
contacts^search,123 |3 | 1
PHP Deprecated:  strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171
 ✔ Rest uri parse with suffix
 ✘ Validation flow
   │
   │ Failed asserting that null matches expected '+256701234567'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:203
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Validation errors
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:226
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Context filtering
   │
   │ Failed asserting that '"id":["0","id","","ID",""],"fullname":["1","fullname","John","Full Name",""]' contains "contacts_k".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:249
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Deprecated: strlen(): Passing null to parameter #1 ($string) of type string is deprecated in /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php on line 2171

 ✔ Session handling
    +-- [invalid] test_field TEST_ERROR
 ✔ Error handling
 ✔ Utility functions
rest_uri_response_error - 404
 ✔ Response handling
 ✔ Model id generation
 ✔ Kv function

Time: 00:00.437, Memory: 28.00 MB

Summary of non-successful tests:

Session Manager (Tests\Unit\SessionManager)
 ✘ Session read
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:115
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Session id extraction
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'test_session_123'
   │ +'dqj3nkc2j5qgfe7d8fbohjbd9v'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionManagerTest.php:92
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Session (Tests\Unit\Session)
 ✘ Ss read Function
   │
   │ TypeError: mysqli_stmt_init(): Argument #1 ($mysql) must be of type mysqli, null given
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/rest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/lib/session.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/SessionTest.php:93
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ↩ Ss destroy Function
 ↩ Ss gc Function
 ↩ Ss new Function
 ↩ Ss new phone Function
 ↩ Ss Function
 ↩ Auth Function

Api Utils (Tests\Unit\ApiUtils)
 ✘ Api definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:142
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Subs definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:155
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

 ✘ Validation flags
   │
   │ Should have a field with email validation
   │ Failed asserting that null is not null.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:246
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Src enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:255
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Location enum definitions
   │
   │ Failed asserting that null is of type "array".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ApiUtilsTest.php:278
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Context (Tests\Unit\Context)
 ✘ Ctx fv function generates key map
   │
   │ Failed asserting that '' contains "id".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ContextTest.php:71
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ↩ Ctx rights with context filter
 ↩ Ctx function basic
 ↩ Ctx with search filter
 ↩ Ctx f function generates full field info

Database Ops (Tests\Unit\DatabaseOps)
 ✘ Select cols function with computed fields
   │
   │ Failed asserting that 'id,age' contains "YEAR(NOW())".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:213
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Kv with default value
   │
   │ Failed asserting that null matches expected 'default_value'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseOpsTest.php:252
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Database (Tests\Unit\Database)
 ✘ Duplicate field validation
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/DatabaseTest.php:202
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ☢ Select query building

Field Operations (Tests\Unit\FieldOperations)
 ✘ Phone fmt with various inputs
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+256701234567'
   │ +'701234567 '
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:227
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ V e s c with complex content
   │
   │ Failed asserting that '&lt;div class=\"test\"&gt;Content & \"quotes\" with 'apostrophes'&lt;\/div&gt;' contains "&amp;".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:245
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Kv with complex operators
   │
   │ Failed asserting that null matches expected 'fallback'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/FieldOperationsTest.php:273
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ↩ Csv cols k mapping
 ↩ Csv cols v mapping

Index (Tests\Unit\Index)
 ✘ Message in Function
   │
   │ Failed asserting that '' contains "success".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php:321
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

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
   │ Failed asserting that an array has the key 'auth'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ModelTest.php:70
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Request Response (Tests\Unit\RequestResponse)
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

 ✘ Val email edge cases
   │
   │ Failed asserting that 1 matches expected 0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:164
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Val id uniqueness
   │
   │ Failed asserting that actual size 1 matches expected size 100.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:220
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Str 2ts all time periods
   │
   │ Failed asserting that 1768780800 is of type "string".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/RequestResponseTest.php:263
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

Rest Helpers (Tests\Unit\RestHelpers)
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

Validation (Tests\Unit\Validation)
 ✘ Phone validation
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:37
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Phone formatting
   │
   │ Failed asserting that two strings are equal.
   │ --- Expected
   │ +++ Actual
   │ @@ @@
   │ -'+256701234567'
   │ +'256701234567'
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:99
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Valid id generation
   │
   │ Failed asserting that 17688595582045.0 is not equal to 17688595582045.0.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/ValidationTest.php:245
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

File Utils (Tests\Unit\FileUtils)
 ↩ Csv cols k function
 ↩ Csv cols v function

Api Integration (Tests\Integration\ApiIntegration)
 ✘ Validation flow
   │
   │ Failed asserting that null matches expected '+256701234567'.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:203
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Validation errors
   │
   │ Failed asserting that 0 matches expected 1.
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:226
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ✘ Context filtering
   │
   │ Failed asserting that '"id":["0","id","","ID",""],"fullname":["1","fullname","John","Full Name",""]' contains "contacts_k".
   │
   │ /home/runner/work/ai/ai/helplinev1/rest_api/tests/Integration/ApiIntegrationTest.php:249
   │ /home/runner/work/ai/ai/helplinev1/rest_api/vendor/bin/phpunit:122
   │

 ↩ Rest uri parse post request

ERRORS!
Tests: 225, Assertions: 1172, Errors: 2, Failures: 31, Skipped: 15, Risky: 1.

Generating code coverage report in Clover XML format ... PHP Fatal error:  Cannot redeclare copy_from_pabx() (previously declared in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php(114) : eval()'d code:2) in /home/runner/work/ai/ai/helplinev1/rest_api/api/index.php on line 17

Fatal error: Cannot redeclare copy_from_pabx() (previously declared in /home/runner/work/ai/ai/helplinev1/rest_api/tests/Unit/IndexTest.php(114) : eval()'d code:2) in /home/runner/work/ai/ai/helplinev1/rest_api/api/index.php on line 17
No test details available
```

---
*Report generated automatically by GitHub Actions*
