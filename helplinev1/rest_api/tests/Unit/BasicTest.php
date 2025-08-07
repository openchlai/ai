<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

class BasicTest extends TestCase
{
    public function testPhpVersion(): void
    {
        $this->assertGreaterThanOrEqual('7.4', PHP_VERSION);
    }

    public function testBasicAssertion(): void
    {
        $this->assertTrue(true);
        $this->assertEquals(4, 2 + 2);
        $this->assertIsString('hello world');
    }

    public function testModelFileExists(): void
    {
        $modelFile = __DIR__ . '/../../api/model.php';
        $this->assertFileExists($modelFile, 'model.php file should exist');
    }

    public function testRestFileExists(): void
    {
        $restFile = __DIR__ . '/../../lib/rest.php';
        $this->assertFileExists($restFile, 'rest.php file should exist');
    }

    public function testCanIncludeModelFile(): void
    {
        $this->expectNotToPerformAssertions();
        
        // Try to include the model file without errors
        require_once __DIR__ . '/../../api/model.php';
        
        // If we get here without exceptions, the file loaded successfully
    }

    public function testGlobalVariablesExist(): void
    {
        require_once __DIR__ . '/../../api/model.php';
        
        // Access globals from GLOBALS superglobal
        $this->assertArrayHasKey('RESOURCES', $GLOBALS, '$RESOURCES should be defined');
        $this->assertArrayHasKey('RIGHTS_1', $GLOBALS, '$RIGHTS_1 should be defined');
        $this->assertArrayHasKey('yesno_enum', $GLOBALS, '$yesno_enum should be defined');
        
        $this->assertIsArray($GLOBALS['RESOURCES'], '$RESOURCES should be an array');
        $this->assertIsArray($GLOBALS['RIGHTS_1'], '$RIGHTS_1 should be an array');
        $this->assertIsArray($GLOBALS['yesno_enum'], '$yesno_enum should be an array');
        
        // Test specific keys exist
        $this->assertArrayHasKey('contacts', $GLOBALS['RESOURCES']);
        $this->assertArrayHasKey('auth', $GLOBALS['RESOURCES']);
        $this->assertArrayHasKey('cases', $GLOBALS['RESOURCES']);
    }

    public function testRestFunctionsExist(): void
    {
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Test that key functions are defined
        $this->assertTrue(function_exists('__VESC'), '__VESC function should exist');
        $this->assertTrue(function_exists('_G'), '_G function should exist');
        $this->assertTrue(function_exists('_P'), '_P function should exist');
        $this->assertTrue(function_exists('_S'), '_S function should exist');
        $this->assertTrue(function_exists('_rands'), '_rands function should exist');
        $this->assertTrue(function_exists('_phone_fmt'), '_phone_fmt function should exist');
    }

    public function testUtilityFunctions(): void
    {
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Test __VESC function
        $this->assertEquals('test', __VESC('test'));
        $this->assertEquals('&lt;script&gt;', __VESC('<script>'));
        
        // Test _rands function
        $random = _rands(8, 'num');
        $this->assertEquals(8, strlen($random));
        $this->assertMatchesRegularExpression('/^\d{8}$/', $random);
        
        // Test phone formatting
        global $GLOBALS;
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $formatted = _phone_fmt('0701234567');
        $this->assertEquals('+256701234567', $formatted);
    }

    public function testValidationFunctions(): void
    {
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Test email validation
        $this->assertEquals(0, _val_email('test@example.com'));
        $this->assertEquals(1, _val_email('invalid-email'));
        
        // Test phone validation
        $phone = '0701234567';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $phone);
    }
}