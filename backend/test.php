<?php
use PHPUnit\Framework\TestCase;

require_once 'path/to/your/api.php';

class HelplineApiTest extends TestCase
{
    private $db;
    private $db2;

    protected function setUp(): void
    {
        // Mock database connections
        $this->db = $this->createMock(mysqli::class);
        $this->db2 = $this->createMock(mysqli::class);
        
        // Replace global db connections with mocks
        $GLOBALS['db'] = $this->db;
        $GLOBALS['db2'] = $this->db2;
        
        // Set up common config values
        $GLOBALS['THE_DB_USN'] = 'test_user';
        $GLOBALS['THE_DB_NAME'] = 'test_db';
        $GLOBALS['THE_DB_SOCK'] = '/tmp/mysql.sock';
        $GLOBALS['RECORDING_ARCHIVE_URL'] = 'http://archive.test/';
        $GLOBALS['API_GATEWAY_USN'] = 'gateway_user';
        $GLOBALS['API_GATEWAY_PASS'] = 'gateway_pass';
    }

    protected function tearDown(): void
    {
        unset($GLOBALS['db']);
        unset($GLOBALS['db2']);
    }

    public function testCopyFromPabxSuccess()
    {
        $uid = 'test123';
        $mockData = 'test audio data';
        
        // Mock curl response
        $mockResponse = [
            'data' => $mockData,
            'info' => [
                'http_code' => 200,
                'content_type' => 'audio/ogg',
                'size_download' => strlen($mockData)
            ]
        ];
        
        // Replace the muu function with a mock
        $this->replaceFunction('muu', function() use ($mockResponse) {
            return $mockResponse;
        });
        
        // Capture output
        ob_start();
        copy_from_pabx($uid);
        $output = ob_get_clean();
        
        $this->assertEquals($mockData, $output);
    }

    public function testMuuFunction()
    {
        $cmd = 'test';
        $args = 'params';
        $expectedUrl = "http://127.0.0.1:8383/{$cmd}/{$args}";
        
        // Mock curl response
        $mockResponse = [
            'data' => 'response data',
            'info' => ['http_code' => 200]
        ];
        
        // Replace curl functions
        $this->replaceFunction('curl_init', function() use ($expectedUrl) {
            $this->assertEquals($expectedUrl, func_get_args()[0]);
            return 'curl_handle';
        });
        
        $this->replaceFunction('curl_setopt', function() {});
        $this->replaceFunction('curl_exec', function() use ($mockResponse) {
            return $mockResponse['data'];
        });
        $this->replaceFunction('curl_getinfo', function() use ($mockResponse) {
            return $mockResponse['info'];
        });
        $this->replaceFunction('curl_close', function() {});
        $this->replaceFunction('error_log', function() {});
        
        $result = muu($cmd, $args);
        $this->assertEquals($mockResponse, $result);
    }

    public function testNotifyFunction()
    {
        $activity = 'test_activity';
        $assigned_to_id = 123;
        $o = ['src_ts' => time(), 'src' => 'test_source'];
        $p = ['param1' => 'value1'];
        
        // Mock rest_uri_post
        $this->replaceFunction('rest_uri_post', function() use ($activity, $assigned_to_id, $o, $p) {
            $this->assertEquals('activities', func_get_args()[0]);
            $this->assertEquals('', func_get_args()[1]);
            $this->assertNull(func_get_args()[2]);
            $this->assertEquals($o, func_get_args()[3]);
            
            $expectedP = array_merge($p, [
                'action' => 'notif',
                'activity' => $activity,
                'assigned_to_id' => $assigned_to_id
            ]);
            $this->assertEquals($expectedP, func_get_args()[4]);
            
            return 201;
        });
        
        notify($activity, $assigned_to_id, $o, $p);
    }

    public function testMessageOut()
    {
        $o = [
            'src_address' => '254712345678',
            'src_msg' => 'Test message',
            'src_callid' => 'call123'
        ];
        $p = [];
        
        // Mock kurl function
        $this->replaceFunction('kurl', function($url, $timeout, $data, $headers) {
            $this->assertEquals($GLOBALS['API_GATEWAY_SEND_MSG'], $url);
            $this->assertEquals(60, $timeout);
            $this->assertJson($data);
            $this->assertEquals(['Content-Type: application/json'], $headers);
            return true;
        });
        
        // Mock muu function
        $this->replaceFunction('muu', function($cmd, $args) {
            $this->assertEquals('ati', $cmd);
            $this->assertStringContainsString('read?id=', $args);
            return true;
        });
        
        message_out($o, $p);
    }

    public function testAgentActionLogin()
    {
        $_SESSION['cc_user_exten'] = '101';
        $_SESSION['cc_user_role'] = 1;
        
        $o = ['action' => '1'];
        
        // Mock muu calls
        $mockCampaigns = "1,2,";
        $this->replaceFunction('muu', function($service, $params) use ($mockCampaigns) {
            if ($service === 'ami') {
                $this->assertStringContainsString('usr?action=1&usr=101', $params);
                $this->assertStringContainsString('queue='.$mockCampaigns, $params);
            }
            return ['data' => '{}', 'info' => ['http_code' => 200]];
        });
        
        // Mock database query
        $this->replaceFunction('qryp', function($query, $types, $params, $single) {
            if (strpos($query, 'workinghour.campaign_id') !== false) {
                return $this->createMock(mysqli_result::class);
            }
            return [['1', '2']];
        });
        
        $result = _agent($o);
        $this->assertEquals(203, $result);
    }

    public function testChanActionDial()
    {
        $_SESSION['cc_user_exten'] = '101';
        $o = [
            'action' => '2', // Dial
            'exten' => 'CB123',
            'chan' => 'chan1',
            'add' => '102',
            'src_uid' => '123',
            'src_address' => '254712345678'
        ];
        
        $this->replaceFunction('muu', function($service, $params) {
            $this->assertEquals('ami', $service);
            $this->assertStringContainsString('redirect?action=2', $params);
            $this->assertStringContainsString('add=102', $params);
            $this->assertStringContainsString('ref=254712345678', $params);
            return true;
        });
        
        $result = _chan($o);
        $this->assertEquals(202, $result);
    }

    public function testRequestHome()
    {
        $_SERVER['REQUEST_METHOD'] = 'GET';
        $_SERVER['REQUEST_URI'] = '/';
        $_SESSION['cc_user_id'] = 1;
        $_SESSION['cc_user_usn'] = 'testuser';
        $_SESSION['cc_user_exten'] = '101';
        $_SESSION['cc_user_role'] = 1;
        
        // Mock rest_uri_get calls
        $this->replaceFunction('rest_uri_get', function() {
            return 200;
        });
        
        // Mock rest_uri_response
        $this->replaceFunction('rest_uri_response', function() {
            echo '{"test": "data"}';
            return 200;
        });
        
        ob_start();
        $result = _request_();
        $output = ob_get_clean();
        
        $this->assertEquals(200, $result);
        $this->assertJson($output);
    }

    private function replaceFunction($functionName, $newFunction)
    {
        if (function_exists($functionName)) {
            rename_function($functionName, "original_$functionName");
        }
        override_function($functionName, '', "return call_user_func_array(\$GLOBALS['{$functionName}_mock'], func_get_args());");
        $GLOBALS["{$functionName}_mock"] = $newFunction;
    }
}

// Helper functions for function mocking
if (!function_exists('rename_function')) {
    function rename_function($original, $new) {
        $GLOBALS[$new] = $GLOBALS[$original];
        unset($GLOBALS[$original]);
    }
}

if (!function_exists('override_function')) {
    function override_function($name, $args, $code) {
        $GLOBALS[$name] = create_function($args, $code);
    }
}