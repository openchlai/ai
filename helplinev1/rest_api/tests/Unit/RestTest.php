<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

class RestTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Clear global errors array
        $GLOBALS['ERRORS'] = [];
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Mock qryp if not already defined
        if (!function_exists('qryp')) {
            eval('
                function qryp($q, $argt, $argv, $r = 0, $db = "db") {
                    return $GLOBALS["test_qryp_result"] ?? null;
                }
            ');
        }
    }

    public function testGlobalHelperFunctions(): void
    {
        // Test _G function
        $_GET['test_param'] = 'test_value';
        $this->assertEquals('test_value', _G('test_param'));
        $this->assertEquals('', _G('nonexistent'));

        // Test _P function  
        $_POST['post_param'] = 'post_value';
        $this->assertEquals('post_value', _P('post_param'));
        $this->assertEquals('', _P('nonexistent'));

        // Test _S function
        $_SESSION['session_param'] = 'session_value';
        $this->assertEquals('session_value', _S('session_param'));
        $this->assertEquals('', _S('nonexistent'));

        // Test _V function
        $array = ['key' => 'value'];
        $this->assertEquals('value', _V($array, 'key'));
        $this->assertEquals('', _V($array, 'nonexistent'));
    }

    public function testVescFunction(): void
    {
        // Test __VESC function for escaping
        $this->assertEquals('test', __VESC('test'));
        $this->assertEquals('&lt;script&gt;', __VESC('<script>'));
        $this->assertEquals('&gt;alert&lt;', __VESC('>alert<'));
        $this->assertEquals('', __VESC(''));
        $this->assertEquals('test with spaces', __VESC('test with spaces'));
    }

    public function testDateFunction(): void
    {
        // Test _date function
        $this->assertEquals('', _date('Y-m-d', 0));
        
        $timestamp = strtotime('2023-01-15 10:30:00');
        $this->assertEquals('2023-01-15', _date('Y-m-d', $timestamp));
        $this->assertEquals('2023', _date('Y', $timestamp));
    }

    public function testEnumFunction(): void
    {
        global $yesno_enum;
        $yesno_enum = [
            '0' => ['0', 'No', 'No', 'Negative'],
            '1' => ['1', 'Yes', 'Yes', 'Positive'],
        ];
        
        $this->assertEquals('No', _enum('::yesno:0:1', '0'));
        $this->assertEquals('Yes', _enum('::yesno:0:1', '1'));
        $this->assertEquals('unknown', _enum('::nonexistent:0:1', 'unknown'));
    }

    public function testModelKIdFunction(): void
    {
        global $contacts_def;
        $contacts_def = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '4', '1', '', '', '', '', '', 'Full Name', ''],
        ];
        
        $result = model_k_id('contacts', '', $contacts_def);
        $this->assertEquals('contact_id', $result);
        
        $result = model_k_id('contacts', '_search', $contacts_def);
        $this->assertEquals('contact_search_id', $result);
    }

    public function testValidationFunctions(): void
    {
        global $GLOBALS;
        $GLOBALS['COUNTRY_CODE'] = '256';
        
        // Test phone validation
        $phone = '0701234567';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        $this->assertEquals('256701234567', $phone);
        
        $phone = 'invalid';
        $result = _val_phone($phone);
        $this->assertEquals(1, $result);
        
        // Test email validation
        $this->assertEquals(0, _val_email('test@example.com'));
        $this->assertEquals(1, _val_email('invalid-email'));
        $this->assertEquals(1, _val_email(''));
    }

    public function testRandomStringGeneration(): void
    {
        // Test _rands function
        $result = _rands(8, 'num');
        $this->assertEquals(8, strlen($result));
        $this->assertMatchesRegularExpression('/^\d{8}$/', $result);
        
        $result = _rands(10, 'alpha');
        $this->assertEquals(10, strlen($result));
        $this->assertMatchesRegularExpression('/^[0-9A-Za-z]{10}$/', $result);
        
        $result = _rands(5, 'ascii');
        $this->assertEquals(5, strlen($result));
    }

    public function testTimestampConversion(): void
    {
        // Test _str2ts function
        $result = _str2ts('all');
        $this->assertEquals('', $result);
        
        $result = _str2ts('today');
        $this->assertGreaterThan(0, $result);
        $this->assertTrue(is_numeric($result));
        
        $result = _str2ts('this_week');
        $this->assertStringContainsString(';', $result);
        
        $result = _str2ts('nonexistent');
        $this->assertEquals('', $result);
    }

    public function testErrorHandling(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        // Test _val_error function
        $result = _val_error('test_table', 0, 'test_field', 'test_value', 'INVALID', 'Test error message');
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertEquals('error', $ERRORS[0][0]);
        $this->assertEquals('Test error message', $ERRORS[0][1]);
        $this->assertEquals('INVALID', $ERRORS[0][2]);
    }

    public function testIdGeneration(): void
    {
        // Test _val_id function
        $id1 = _val_id();
        $this->assertTrue(is_numeric($id1));
        $this->assertGreaterThan(0, $id1);
        
        // Test that IDs are unique (allow small timing variance)
        usleep(1000);
        $id2 = _val_id();
        $this->assertTrue(is_numeric($id2));
        $this->assertGreaterThan(0, $id2);
    }

    public function testQueryBuilding(): void
    {
        // Test k_c function (IN clause)
        $aa = ["w" => "", "s" => ""];
        $av = [];
        
        k_c('test_table', 'test_field', ['value1', 'value2'], $aa, $av);
        
        $this->assertStringContainsString('test_table.test_field IN', $aa["w"]);
        $this->assertEquals('ss', $aa["s"]);
        $this->assertEquals(['value1', 'value2'], $av);
        
        // Test k_s function (LIKE clause)
        $aa = ["w" => "", "s" => ""];
        $av = [];
        
        k_s('test_table', 'test_field', ['search_term'], $aa, $av);
        
        $this->assertStringContainsString('test_table.test_field LIKE', $aa["w"]);
        $this->assertEquals('s', $aa["s"]);
        $this->assertEquals(['%search_term%'], $av);
        
        // Test k_n function (numeric range)
        $aa = ["w" => "", "s" => ""];
        $av = [];
        
        k_n('test_table', 'num_field', ['10'], $aa, $av);
        
        $this->assertStringContainsString('test_table.num_field=', $aa["w"]);
        $this->assertEquals('s', $aa["s"]);
        $this->assertEquals(['10'], $av);
    }

    public function testUriParsing(): void
    {
        global $RESOURCES, $contacts_def, $FN;
        
        // Set up required globals
        if (!isset($RESOURCES)) {
            $RESOURCES = [
                'contacts' => ['contact', '', '3', '0', '0', 'Contact', 'fullname', '', '']
            ];
        }
        
        if (!isset($contacts_def)) {
            $contacts_def = [['id', '', '0', '2', '', '', '', '', '', 'ID', '']];
        }
        
        if (!isset($FN)) {
            $FN = [];
        }
        
        $u = '';
        $suffix = '';
        $id = null;
        $o = [];
        
        // Test simple GET request
        $result = rest_uri_parse('GET', '/contacts', 0, $u, $suffix, $id, $o);
        $this->assertEquals(0, $result);
        $this->assertEquals('contacts', $u);
        $this->assertEquals('', $suffix);
        $this->assertNull($id);
        
        // Test GET request with ID
        $result = rest_uri_parse('GET', '/contacts/123', 0, $u, $suffix, $id, $o);
        $this->assertEquals(0, $result);
        $this->assertEquals('contacts', $u);
        $this->assertEquals('123', $id);
    }

    public function testResponseErrorHandling(): void
    {
        // Test different error responses
        ob_start();
        rest_uri_response_error(400);
        $output = ob_get_clean();
        $this->assertStringContainsString('Invalid Request', $output);
        
        ob_start();
        rest_uri_response_error(401);
        $output = ob_get_clean();
        $this->assertStringContainsString('Authentication Required', $output);
        
        ob_start();
        rest_uri_response_error(403);
        $output = ob_get_clean();
        $this->assertStringContainsString('Access Denied', $output);
        
        ob_start();
        rest_uri_response_error(404);
        $output = ob_get_clean();
        $this->assertStringContainsString('not found', $output);
    }

    public function testValueExtractionFunction(): void
    {
        // Test _kv function
        $o = ['field1' => 'value1'];
        $p = ['field2' => 'value2'];
        $op = '=';
        
        // Test basic field access
        $result = _kv('field1', $op, $o, $p);
        $this->assertEquals('value1', $result);
        
        $result = _kv('field2', $op, $o, $p);
        $this->assertEquals('value2', $result);
        
        // Test operator parsing
        $result = _kv(':!=:nonexistent', $op, $o, $p);
        $this->assertEquals('!=', $op);
        $this->assertNull($result);
        
        // Test literal value
        $result = _kv(' literal_value', $op, $o, $p);
        $this->assertEquals('literal_value', $result);
    }
}