<?php

namespace Tests\Unit;

use Tests\TestCase;

class ApiUtilsTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Set up test environment
        $this->setUpTestEnvironment();
    }

    private function setUpTestEnvironment(): void
    {
        // Set up required global variables
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $GLOBALS['ERRORS'] = [];
        
        // Set up resource definitions
        global $RESOURCES, $METRICS;
        
        $RESOURCES = [
            'test_resource' => ['test_table', 'test_alias', '3', '0', '0', 'Test Resource', 'id DESC', '', '']
        ];
        
        $METRICS = [
            'case_count' => ['COUNT(DISTINCT kase.id)', '', '', '', '', '', ''],
            'call_count' => ['COUNT(DISTINCT chan.id)', '', '', '', '', '', ''],
            'client_count' => ['COUNT(DISTINCT client.id)', '', '', '', '', '', '']
        ];
        
        // Set up test field definitions
        global $test_resource_def;
        $test_resource_def = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['name', '', '3', '1', 'm', '', '', '', '', 'Name', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''],
            ['status', '', '3', '2', 'v', '', '', '1', '', 'Status', ''],
            ['created_on', '', '0', '3', '', '', '', '', '', 'Created On', '']
        ];
    }

    public function testResourceDefinitions(): void
    {
        global $RESOURCES;
        
        $this->assertIsArray($RESOURCES);
        $this->assertArrayHasKey('test_resource', $RESOURCES);
        
        $resource = $RESOURCES['test_resource'];
        $this->assertEquals('test_table', $resource[0]); // Table name
        $this->assertEquals('test_alias', $resource[1]); // Alias
        $this->assertEquals('Test Resource', $resource[5]); // Display name
    }

    public function testMetricsDefinitions(): void
    {
        global $METRICS;
        
        $this->assertIsArray($METRICS);
        $this->assertArrayHasKey('case_count', $METRICS);
        $this->assertArrayHasKey('call_count', $METRICS);
        
        $caseMetric = $METRICS['case_count'];
        $this->assertStringContainsString('COUNT', $caseMetric[0]);
        $this->assertStringContainsString('kase.id', $caseMetric[0]);
    }

    public function testRightsSystemStructure(): void
    {
        // Test that rights arrays exist and have proper structure
        if (isset($GLOBALS['RIGHTS_1'])) {
            $this->assertIsArray($GLOBALS['RIGHTS_1']);
        } else {
            $this->markTestSkipped('RIGHTS_1 not defined in this test context');
        }
        
        if (isset($GLOBALS['RIGHTS_2'])) {
            $this->assertIsArray($GLOBALS['RIGHTS_2']);
        }
        
        if (isset($GLOBALS['RIGHTS_99'])) {
            $this->assertIsArray($GLOBALS['RIGHTS_99']);
        }
        
        // Test rights structure for a resource
        if (isset($GLOBALS['RIGHTS_1']['contacts'])) {
            $rights = $GLOBALS['RIGHTS_1']['contacts'];
            $this->assertIsArray($rights);
            $this->assertGreaterThanOrEqual(5, count($rights)); // Should have at least 5 permission flags
        }
    }

    public function testEnumDefinitions(): void
    {
        // Test yesno enum if available
        if (isset($GLOBALS['yesno_enum'])) {
            $this->assertIsArray($GLOBALS['yesno_enum']);
            $this->assertArrayHasKey('0', $GLOBALS['yesno_enum']);
            $this->assertArrayHasKey('1', $GLOBALS['yesno_enum']);
            $this->assertEquals('No', $GLOBALS['yesno_enum']['0'][1]);
            $this->assertEquals('Yes', $GLOBALS['yesno_enum']['1'][1]);
        }
        
        // Test role enum if available
        if (isset($GLOBALS['role_enum'])) {
            $this->assertIsArray($GLOBALS['role_enum']);
            $this->assertArrayHasKey('1', $GLOBALS['role_enum']);
            $this->assertEquals('Counsellor', $GLOBALS['role_enum']['1'][1]);
        }
        
        // Test vector enum if available
        if (isset($GLOBALS['vector_enum'])) {
            $this->assertIsArray($GLOBALS['vector_enum']);
            $this->assertArrayHasKey('1', $GLOBALS['vector_enum']);
            $this->assertArrayHasKey('2', $GLOBALS['vector_enum']);
            $this->assertEquals('Inbound', $GLOBALS['vector_enum']['1'][1]);
            $this->assertEquals('Outbound', $GLOBALS['vector_enum']['2'][1]);
        }
        
        // If none are available, mark test as skipped
        if (!isset($GLOBALS['yesno_enum']) && !isset($GLOBALS['role_enum']) && !isset($GLOBALS['vector_enum'])) {
            $this->markTestSkipped('No enum definitions available in test context');
        }
    }

    public function testApiDefinitions(): void
    {
        global $contacts_api, $auth_api, $cases_api;
        
        $this->assertIsArray($contacts_api);
        $this->assertIsArray($auth_api);
        $this->assertIsArray($cases_api);
        
        // Each API should have field mappings
        $this->assertGreaterThan(0, count($contacts_api));
        $this->assertGreaterThan(0, count($auth_api));
        $this->assertGreaterThan(0, count($cases_api));
    }

    public function testSubsDefinitions(): void
    {
        global $contacts_subs, $cases_subs, $activities_subs;
        
        $this->assertIsArray($contacts_subs);
        $this->assertIsArray($cases_subs);
        $this->assertIsArray($activities_subs);
        
        // Test subs structure - each should define related table operations
        foreach ($cases_subs as $sub) {
            $this->assertIsArray($sub);
            $this->assertGreaterThanOrEqual(3, count($sub));
        }
    }

    public function testJoinDefinitions(): void
    {
        global $contacts_join, $cases_join, $calls_join;
        
        $this->assertIsArray($contacts_join);
        $this->assertIsArray($cases_join);
        $this->assertIsArray($calls_join);
        
        // Test join structure
        foreach ($cases_join as $joinKey => $joinDef) {
            $this->assertIsArray($joinDef);
            $this->assertEquals(3, count($joinDef)); // [table, alias, condition]
            $this->assertIsString($joinDef[0]); // Table
            $this->assertIsString($joinDef[1]); // Alias
            $this->assertIsString($joinDef[2]); // Condition
        }
    }

    public function testCsvDefinitions(): void
    {
        global $contacts_csv, $cases_csv, $calls_csv;
        
        $this->assertIsArray($contacts_csv);
        $this->assertIsArray($cases_csv);
        $this->assertIsArray($calls_csv);
        
        // Test that CSV definitions contain expected fields
        $this->assertContains('id', $cases_csv);
        $this->assertContains('created_on', $cases_csv);
        $this->assertContains('uniqueid', $calls_csv);
        $this->assertContains('fullname', $contacts_csv);
    }

    public function testDuplicateCheckDefinitions(): void
    {
        global $contacts_dup, $auth_dup, $otp_dup;
        
        $this->assertIsArray($contacts_dup);
        $this->assertIsArray($auth_dup);
        $this->assertIsArray($otp_dup);
        
        // Test duplicate check structure
        $this->assertGreaterThanOrEqual(4, count($contacts_dup));
        $this->assertEquals('contact', $contacts_dup[0]); // Table
        $this->assertEquals('dup', $contacts_dup[2]); // Operation
    }

    public function testFieldDefinitionStructure(): void
    {
        global $contacts_def, $auth_def, $cases_def;
        
        $this->assertIsArray($contacts_def);
        $this->assertIsArray($auth_def);
        $this->assertIsArray($cases_def);
        
        // Test field definition structure
        foreach ($contacts_def as $field) {
            $this->assertIsArray($field);
            $this->assertGreaterThanOrEqual(10, count($field)); // Should have all required elements
            $this->assertIsString($field[0]); // Field name
            $this->assertIsString($field[9]); // Display name
        }
    }

    public function testValidationFlags(): void
    {
        global $contacts_def;
        
        // Find fields with specific validation flags
        $phoneField = null;
        $emailField = null;
        $mandatoryField = null;
        
        foreach ($contacts_def as $field) {
            if ($field[5] === 'p') $phoneField = $field;
            if ($field[5] === 'e') $emailField = $field;
            if ($field[4] === 'm') $mandatoryField = $field;
        }
        
        $this->assertNotNull($phoneField, 'Should have a field with phone validation');
        $this->assertNotNull($emailField, 'Should have a field with email validation');
        $this->assertNotNull($mandatoryField, 'Should have a mandatory field');
    }

    public function testSrcEnumDefinitions(): void
    {
        global $src_enum, $hangup_status_enum, $sla_enum;
        
        $this->assertIsArray($src_enum);
        $this->assertIsArray($hangup_status_enum);
        $this->assertIsArray($sla_enum);
        
        // Test src enum structure
        foreach ($src_enum as $key => $value) {
            $this->assertIsArray($value);
            $this->assertGreaterThanOrEqual(4, count($value));
        }
        
        // Test hangup status enum
        $this->assertArrayHasKey('0', $hangup_status_enum);
        $this->assertArrayHasKey('5', $hangup_status_enum);
        $this->assertEquals('answered', $hangup_status_enum['5'][1]);
        
        // Test SLA enum
        $this->assertArrayHasKey('0', $sla_enum);
        $this->assertEquals('0-20s', $sla_enum['0'][1]);
    }

    public function testLocationEnumDefinitions(): void
    {
        global $nationality_enum, $tribe_enum, $lang_enum;
        
        $this->assertIsArray($nationality_enum);
        $this->assertIsArray($tribe_enum);
        $this->assertIsArray($lang_enum);
        
        // Test structure of location-related enums
        foreach ($nationality_enum as $key => $value) {
            $this->assertIsArray($value);
            $this->assertCount(3, $value); // [key, display_name, extra]
        }
    }

    public function testSpecialFieldDefinitions(): void
    {
        global $cases_def;
        
        // Look for special field types in cases
        $computedField = null;
        $joinField = null;
        
        foreach ($cases_def as $field) {
            if ($field[2] === '4') $computedField = $field; // Computed field
            if (strlen($field[6]) > 0) $joinField = $field; // Join field
        }
        
        $this->assertNotNull($computedField, 'Should have computed fields');
        $this->assertNotNull($joinField, 'Should have join fields');
    }

    public function testSystemConstants(): void
    {
        global $DISPOSITION_ID_COMPLETE, $DISPOSITION_ROOT_ID, $AGE_GROUP_ROOT_ID;
        
        // Test that system constants are defined
        $this->assertIsString($DISPOSITION_ID_COMPLETE);
        $this->assertIsString($DISPOSITION_ROOT_ID);
        $this->assertIsString($AGE_GROUP_ROOT_ID);
        
        $this->assertNotEmpty($DISPOSITION_ID_COMPLETE);
        $this->assertNotEmpty($DISPOSITION_ROOT_ID);
        $this->assertNotEmpty($AGE_GROUP_ROOT_ID);
    }

    public function testDispositionDefinitions(): void
    {
        global $dispositions_def, $dispositions_api;
        
        $this->assertIsArray($dispositions_def);
        $this->assertIsArray($dispositions_api);
        
        // Test disposition field structure
        foreach ($dispositions_def as $field) {
            $this->assertIsArray($field);
            $this->assertIsString($field[0]); // Field name
        }
    }

    public function testActivityDefinitions(): void
    {
        global $activities_def, $activities_api;
        
        $this->assertIsArray($activities_def);
        $this->assertIsArray($activities_api);
        
        // Check for key activity fields
        $srcField = null;
        $timestampField = null;
        
        foreach ($activities_def as $field) {
            if ($field[0] === 'src') $srcField = $field;
            if ($field[0] === 'src_ts') $timestampField = $field;
        }
        
        $this->assertNotNull($srcField, 'Activities should have src field');
        $this->assertNotNull($timestampField, 'Activities should have timestamp field');
    }

    public function testMessageDefinitions(): void
    {
        global $messages_def, $pmessages_def;
        
        $this->assertIsArray($messages_def);
        $this->assertIsArray($pmessages_def);
        
        // Check for key message fields
        $vectorField = null;
        $mimeField = null;
        
        foreach ($messages_def as $field) {
            if ($field[0] === 'src_vector') $vectorField = $field;
            if ($field[0] === 'src_mime') $mimeField = $field;
        }
        
        $this->assertNotNull($vectorField, 'Messages should have vector field');
        $this->assertNotNull($mimeField, 'Messages should have mime field');
    }

    public function testCallDefinitions(): void
    {
        global $calls_def, $chanss_def;
        
        $this->assertIsArray($calls_def);
        $this->assertIsArray($chanss_def);
        
        // Check for key call fields
        $phoneField = null;
        $hangupField = null;
        $durationField = null;
        
        foreach ($calls_def as $field) {
            if ($field[0] === 'phone') $phoneField = $field;
            if ($field[0] === 'hangup_status') $hangupField = $field;
            if ($field[0] === 'talk_time') $durationField = $field;
        }
        
        $this->assertNotNull($phoneField, 'Calls should have phone field');
        $this->assertNotNull($hangupField, 'Calls should have hangup status field');
        $this->assertNotNull($durationField, 'Calls should have duration field');
    }
}
