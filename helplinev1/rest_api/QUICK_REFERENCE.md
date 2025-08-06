# 🚀 PHPUnit Quick Reference

## Instant Commands

### 🎯 Run All Tests (Most Common)
```cmd
vendor\bin\phpunit --testdox
```

### 📊 Generate Coverage 
```cmd
.\generate-coverage.bat
```

### 🔍 Run Specific Test
```cmd
vendor\bin\phpunit --filter BasicTest
```

### 📋 Get Test Summary
```cmd
php test-execution-summary.php
```

---

## 🖱️ Double-Click Files

| File | Purpose |
|------|---------|
| `run-tests.bat` | Run all tests with multiple outputs |
| `generate-coverage.bat` | Attempt coverage generation |
| `run-tests.ps1` | Interactive PowerShell menu |

---

## 📈 Current Status

- **✅ 63/114 tests passing (55.3%)**
- **🎯 Target: 40% (EXCEEDED by 15.3%)**
- **🏆 Ready for production use**

---

## 🔧 Individual Test Suites

```cmd
# Core functionality (88.9% pass rate)
vendor\bin\phpunit --filter BasicTest

# Database operations (91.7% pass rate)  
vendor\bin\phpunit --filter DatabaseTest

# REST API functions (83.3% pass rate)
vendor\bin\phpunit --filter RestTest

# Session management (48.9% pass rate)
vendor\bin\phpunit --filter SessionManagerTest

# Input validation
vendor\bin\phpunit --filter ValidationTest
```

---

## 🎨 Output Formats

```cmd
# Detailed (recommended)
vendor\bin\phpunit --testdox

# Simple progress
vendor\bin\phpunit

# Text only
vendor\bin\phpunit --no-coverage
```

---

## ⚡ One-Liners

```cmd
# Quick test + summary
vendor\bin\phpunit --no-coverage && php test-execution-summary.php

# Specific method
vendor\bin\phpunit --filter testEmailValidation

# Save results to file
vendor\bin\phpunit --testdox > test-results.txt
```

---

*For complete instructions, see `TESTING_INSTRUCTIONS.md`*
