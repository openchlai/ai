<?php

namespace Tests\Integration;

use Tests\TestCase;

class ApiIntegrationTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        require_once __DIR__ . '/../../lib/session.php';
        
        // Set up minimal globals
        $this->setUpGlobalVariables();
        $this->setUpUserSession();
    }

    private function setUpGlobalVariables(): void
    {
        global $RESOURCES, $RIGHTS_1, $RIGHTS_99, $contacts_def, $contacts_k, $auth_def, $cases_def;
        global $contacts_api, $users_api, $FN;
        
        if (!isset($RESOURCES)) {
            $RESOURCES = [
                "contacts" => ["contact", "", "3", "0", "0", "Contact", "fullname", "", ""],
                "auth" => ["auth", "user", "3", "0", "0", "User", "", "", ""],
                "cases" => ["kase", "case", "3", "0", "0", "Case", "", "", ""],
            ];
        }

        if (!isset($RIGHTS_1)) {
            $RIGHTS_1 = [
                "contacts" => ["1", "1", "1", "0", "0"],
                "auth" => ["1", "0", "0", "0", "0"],
                "cases" => ["1", "1", "1", "1", "0"],
            ];
            $RIGHTS_99 = $RIGHTS_1;
        }

        if (!isset($contacts_def)) {
            $contacts_def = [
                ["id", "", "0", "2", "", "", "", "", "", "ID", ""],
                ["fullname", "", "4", "1", "", "", "", "", "", "Full Name", ""],
                ["phone", "", "3", "1", "", "p", "", "", "", "Phone", ""],
                ["email", "", "3", "2", "", "e", "", "", "", "Email", ""],
                ["created_on", "", "0", "3", "", "", "", "", "", "Created On", ""],
            ];

            $contacts_k = [
                "id" => 0,
                "fullname" => 1, 
                "phone" => 2,
                "email" => 3,
                "created_on" => 4,
            ];
        }

        if (!isset($auth_def)) {
            $auth_def = [
                ["id", "", "0", "2", "", "", "", "", "", "ID", ""],
                ["usn", "", "3", "2", "u", "", "", "", "", "Username", ""],
                ["role", "", "3", "2", "m", "", "", "", "", "Role", ""],
                ["created_on", "", "0", "3", "", "", "", "", "", "Created On", ""],
            ];
        }

        if (!isset($cases_def)) {
            $cases_def = [
                ["id", "", "0", "2", "", "", "", "", "", "CASE ID", ""],
                ["created_on", "", "0", "3", "", "", "", "", "", "Created On", ""],
                ["priority", "", "3", "2", "m", "", "", "", "", "Priority", ""],
                ["status", "", "3", "2", "m", "", "", "", "", "Status", ""],
                ["narrative", "", "3", "1", "m", "", "", "", "", "Narrative", ""],
            ];
        }

        if (!isset($contacts_api)) {
            $contacts_api = [
                ["contacts", "", ""],
            ];
        }

        if (!isset($users_api)) {
            $users_api = [
                ["users", "", ""],
            ];
        }

        if (!isset($FN)) {
            $FN = [
                "sendOTP" => 1,
                "verifyOTP" => 1,
                "resetAuth" => 1,
                "changeAuth" => 1,
                "dash" => 1,
                "wallonly" => 1,
                "agent" => 1,
                "chan" => 1,
            ];
        }
    }

    public function testRestUriParseGetRequest(): void
    {
        $u = '';
        $suffix = '';
        $id = null;
        $o = [];
        
        $result = rest_uri_parse('GET', '/contacts/123', 0, $u, $suffix, $id, $o);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('contacts', $u);
        $this->assertEquals('123', $id);
        $this->assertArrayHasKey('contact_id', $o);
        $this->assertEquals('123', $o['contact_id']);
    }

    public function testRestUriParsePostRequest(): void
    {
        $u = '';
        $suffix = '';
        $id = null;
        $o = [];
        
        // Mock JSON input
        $jsonData = ['fullname' => 'John Doe', 'email' => 'john@example.com'];
        
        // Mock file_get_contents for POST data
        eval('
            function file_get_contents($filename) {
                if ($filename === "php://input") {
                    return \'{"fullname":"John Doe","email":"john@example.com"}\';
                }
                return false;
            }
        ');
        
        $_SERVER['CONTENT_TYPE'] = 'application/json';
        $result = rest_uri_parse('POST', '/contacts', 0, $u, $suffix, $id, $o);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('contacts', $u);
        $this->assertNull($id);
        $this->assertEquals('John Doe', $o['fullname']);
        $this->assertEquals('john@example.com', $o['email']);
    }

    public function testRestUriParseInvalidResource(): void
    {
        $u = '';
        $suffix = '';
        $id = null;
        $o = [];
        
        $result = rest_uri_parse('GET', '/nonexistent/123', 0, $u, $suffix, $id, $o);
        
        $this->assertEquals(404, $result);
    }

    public function testRestUriParseWithSuffix(): void
    {
        $u = '';
        $suffix = '';
        $id = null;
        $o = [];
        
        $result = rest_uri_parse('GET', '/contacts^search/123', 0, $u, $suffix, $id, $o);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('contacts', $u);
        $this->assertEquals('_search', $suffix);
        $this->assertEquals('123', $id);
    }

    public function testValidationFlow(): void
    {
        global $contacts_def;
        
        // Test successful validation
        $u = 'contacts';
        $id = null;
        $o = ['fullname' => 'John Doe', 'phone' => '0701234567', 'email' => 'john@example.com'];
        $p = [];
        $a = $contacts_def[1]; // fullname field
        $v = null;
        
        $result = _val($u, $id, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('John Doe', $v);
        
        // Test phone validation
        $a = $contacts_def[2]; // phone field
        $result = _val($u, $id, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $v);
        
        // Test email validation
        $a = $contacts_def[3]; // email field
        $result = _val($u, $id, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('john@example.com', $v);
    }

    public function testValidationErrors(): void
    {
        global $contacts_def, $ERRORS;
        
        $ERRORS = [];
        $u = 'contacts';
        $id = null;
        $o = ['phone' => 'invalid-phone', 'email' => 'invalid-email', 'i_' => 0];
        $p = [];
        
        // Test invalid phone
        $a = $contacts_def[2]; // phone field
        $v = null;
        $result = _val($u, $id, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
        $this->assertHasError('Invalid Phone Number');
        
        // Test invalid email
        $ERRORS = [];
        $a = $contacts_def[3]; // email field
        $result = _val($u, $id, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
        $this->assertHasError('Invalid Email address');
    }

    public function testContextFiltering(): void
    {
        global $contacts_def;
        
        $aa = ["f" => "", "w" => "", "s" => "", "ta" => ""];
        $av = [];
        $fo = ['fullname' => 'John', 'phone' => '070'];
        $join = [];
        
        ctx_f('contacts', $aa, $av, $fo);
        
        $this->assertNotEmpty($aa["f"]);
        $this->assertStringContainsString('contacts_k', $aa["f"]);
    }

    public function testSessionHandling(): void
    {
        // Test session ID extraction from Bearer token
        $_SERVER['HTTP_AUTHORIZATION'] = 'Bearer abc123token';
        $result = ss_id('default_session');
        $this->assertEquals('abc123token', $result);
        
        // Test session ID without auth header
        unset($_SERVER['HTTP_AUTHORIZATION']);
        $result = ss_id('default_session');
        $this->assertIsString($result);
    }

    public function testErrorHandling(): void
    {
        global $ERRORS;
        
        $ERRORS = [];
        
        // Test error creation
        _val_error('test_table', 0, 'test_field', 'test_value', 'TEST_ERROR', 'Test error message');
        
        $this->assertCount(1, $ERRORS);
        $this->assertEquals('error', $ERRORS[0][0]);
        $this->assertEquals('Test error message', $ERRORS[0][1]);
        $this->assertEquals('TEST_ERROR', $ERRORS[0][2]);
        $this->assertEquals('test_table', $ERRORS[0][3]);
        $this->assertEquals('test_field', $ERRORS[0][5]);
    }

    public function testUtilityFunctions(): void
    {
        // Test phone formatting
        global $GLOBALS;
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        $this->assertEquals('+256701234567', _phone_fmt('0701234567'));
        $this->assertEquals('+256701234567', _phone_fmt('701234567'));
        
        // Test random string generation
        $random = _rands(10, 'num');
        $this->assertEquals(10, strlen($random));
        $this->assertMatchesRegularExpression('/^\d{10}$/', $random);
        
        // Test date formatting
        $this->assertEquals('', _date('Y-m-d', 0));
        $timestamp = strtotime('2023-01-01');
        $this->assertEquals('2023-01-01', _date('Y-m-d', $timestamp));
        
        // Test value escaping
        $this->assertEquals('test', __VESC('test'));
        $this->assertEquals('&lt;script&gt;', __VESC('<script>'));
    }

    public function testResponseHandling(): void
    {
        // Test various HTTP response codes
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

    public function testModelIdGeneration(): void
    {
        global $contacts_def;
        
        $result = model_k_id('contacts', '', $contacts_def);
        $this->assertEquals('contact_id', $result);
        
        $result = model_k_id('contacts', '_search', $contacts_def);
        $this->assertEquals('contact_search_id', $result);
    }

    public function testKvFunction(): void
    {
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