#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

/**
 * Enhanced test runner for VitePress documentation
 */
class TestRunner {
  constructor() {
    this.testResults = {
      passed: 0,
      failed: 0,
      coverage: null,
      startTime: Date.now()
    }
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString()
    const colors = {
      info: '\x1b[36m',    // Cyan
      success: '\x1b[32m', // Green
      error: '\x1b[31m',   // Red
      warning: '\x1b[33m', // Yellow
      reset: '\x1b[0m'
    }

    console.log(`${colors[type]}[${timestamp}] ${message}${colors.reset}`)
  }

  async runCommand(command, description) {
    this.log(`Running: ${description}`)
    try {
      const output = execSync(command, { 
        stdio: 'pipe', 
        encoding: 'utf8',
        cwd: process.cwd()
      })
      this.log(`✓ ${description} completed`, 'success')
      return output
    } catch (error) {
      this.log(`✗ ${description} failed: ${error.message}`, 'error')
      throw error
    }
  }

  async checkDependencies() {
    this.log('Checking dependencies...', 'info')
    
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'))
    const requiredDeps = [
      'vitest',
      '@vitest/ui', 
      'jsdom',
      '@testing-library/jest-dom'
    ]

    const missingDeps = requiredDeps.filter(dep => 
      !packageJson.devDependencies?.[dep] && !packageJson.dependencies?.[dep]
    )

    if (missingDeps.length > 0) {
      this.log(`Missing dependencies: ${missingDeps.join(', ')}`, 'warning')
      this.log('Installing missing dependencies...', 'info')
      
      try {
        await this.runCommand(
          `npm install --save-dev ${missingDeps.join(' ')}`,
          'Installing dependencies'
        )
      } catch (error) {
        this.log('Failed to install dependencies. Please install manually:', 'error')
        this.log(`npm install --save-dev ${missingDeps.join(' ')}`, 'info')
        process.exit(1)
      }
    }

    this.log('Dependencies check completed', 'success')
  }

  async createRequiredDirectories() {
    const dirs = ['tests', 'utils', 'scripts']
    
    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
        this.log(`Created directory: ${dir}`, 'info')
      }
    }
  }

  async validateTestSetup() {
    this.log('Validating test setup...', 'info')
    
    const requiredFiles = [
      'vitest.config.ts',
      'tests/setup.ts',
      'tests/config.test.ts',
      'tests/content.test.ts',
      'tests/utils.test.ts',
      'tests/navigation.test.ts',
      'tests/integration.test.ts',
      'utils/docs.ts'
    ]

    const missingFiles = requiredFiles.filter(file => !fs.existsSync(file))
    
    if (missingFiles.length > 0) {
      this.log(`Missing test files: ${missingFiles.join(', ')}`, 'warning')
      this.log('Please ensure all test files are created properly', 'error')
      return false
    }

    this.log('Test setup validation completed', 'success')
    return true
  }

  async runUnitTests() {
    this.log('Running unit tests...', 'info')
    
    try {
      const output = await this.runCommand(
        'npx vitest run --reporter=verbose',
        'Unit tests execution'
      )
      
      // Parse test results
      const lines = output.split('\n')
      const summaryLine = lines.find(line => line.includes('Test Files'))
      
      if (summaryLine) {
        this.log(`Test Summary: ${summaryLine.trim()}`, 'info')
      }
      
      return true
    } catch (error) {
      this.log('Unit tests failed', 'error')
      return false
    }
  }

  async runCoverageTest() {
    this.log('Running coverage analysis...', 'info')
    
    try {
      const output = await this.runCommand(
        'npx vitest run --coverage',
        'Coverage analysis'
      )
      
      // Extract coverage information
      const lines = output.split('\n')
      const coverageLine = lines.find(line => 
        line.includes('All files') && line.includes('%')
      )
      
      if (coverageLine) {
        const coverageMatch = coverageLine.match(/(\d+\.\d+)%/)
        if (coverageMatch) {
          const coverage = parseFloat(coverageMatch[1])
          this.testResults.coverage = coverage
          
          if (coverage >= 40) {
            this.log(`✓ Coverage target met: ${coverage}%`, 'success')
          } else {
            this.log(`⚠ Coverage below target: ${coverage}% (target: 40%)`, 'warning')
          }
        }
      }
      
      return true
    } catch (error) {
      this.log('Coverage analysis failed', 'error')
      return false
    }
  }

  async generateReport() {
    const endTime = Date.now()
    const duration = (endTime - this.testResults.startTime) / 1000

    this.log('Generating test report...', 'info')
    
    const report = {
      timestamp: new Date().toISOString(),
      duration: `${duration}s`,
      coverage: this.testResults.coverage,
      status: this.testResults.coverage >= 40 ? 'PASSED' : 'NEEDS_IMPROVEMENT',
      recommendations: []
    }

    if (this.testResults.coverage < 40) {
      report.recommendations.push('Increase test coverage to meet 40% minimum requirement')
      report.recommendations.push('Add more unit tests for utility functions')
      report.recommendations.push('Consider adding integration tests for complex workflows')
    }

    // Write report to file
    fs.writeFileSync('test-report.json', JSON.stringify(report, null, 2))
    
    this.log('='.repeat(60), 'info')
    this.log('TEST EXECUTION SUMMARY', 'info')
    this.log('='.repeat(60), 'info')
    this.log(`Status: ${report.status}`, report.status === 'PASSED' ? 'success' : 'warning')
    this.log(`Duration: ${report.duration}`, 'info')
    this.log(`Coverage: ${report.coverage}%`, report.coverage >= 40 ? 'success' : 'warning')
    this.log('='.repeat(60), 'info')

    if (report.recommendations.length > 0) {
      this.log('RECOMMENDATIONS:', 'warning')
      report.recommendations.forEach(rec => this.log(`• ${rec}`, 'warning'))
      this.log('='.repeat(60), 'info')
    }

    return report
  }

  async run() {
    try {
      this.log('Starting VitePress Documentation Test Suite', 'info')
      
      await this.checkDependencies()
      await this.createRequiredDirectories()
      
      const setupValid = await this.validateTestSetup()
      if (!setupValid) {
        process.exit(1)
      }

      const testsPass = await this.runUnitTests()
      await this.runCoverageTest()
      
      const report = await this.generateReport()
      
      if (testsPass && report.status === 'PASSED') {
        this.log('All tests completed successfully! 🎉', 'success')
        process.exit(0)
      } else {
        this.log('Some tests failed or coverage is insufficient', 'warning')
        process.exit(1)
      }
      
    } catch (error) {
      this.log(`Test execution failed: ${error.message}`, 'error')
      process.exit(1)
    }
  }
}

// Run the test suite
const runner = new TestRunner()
runner.run()