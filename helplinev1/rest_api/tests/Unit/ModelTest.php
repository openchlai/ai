<?php

namespace Tests\Unit;

use Tests\TestCase;

class ModelTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include the model file
        require_once __DIR__ . '/../../api/model.php';
        
        // Set up required global variables from model.php
        global $RESOURCES, $RIGHTS_1, $RIGHTS_99;
        if (!isset($RESOURCES)) {
            $this->setUpGlobalVariables();
        }
    }

    private function setUpGlobalVariables(): void
    {
        // Set up minimal required global variables for testing
        global $RESOURCES, $RIGHTS_1, $RIGHTS_99, $auth_def, $contacts_def;
        
        $RESOURCES = [
            "auth" => ["auth", "user", "3", "0", "0", "User", "", "", ""],
            "contacts" => ["contact", "", "3", "0", "0", "Contact", "fullname", "", ""],
            "cases" => ["kase", "case", "3", "0", "0", "Case", "", "", ""],
        ];

        $RIGHTS_1 = [
            "auth" => ["1", "0", "0", "0", "0"],
            "contacts" => ["1", "1", "1", "0", "0"],
            "cases" => ["1", "1", "1", "1", "0"],
        ];

        $RIGHTS_99 = $RIGHTS_1;

        // Define some basic field definitions
        $auth_def = [
            ["id", "", "0", "2", "", "", "", "", "", "ID", ""],
            ["usn", "", "3", "2", "u", "", "", "", "", "Username", ""],
            ["role", "", "3", "2", "m", "", "", "", "", "Role", ""],
        ];

        $contacts_def = [
            ["id", "", "0", "2", "", "", "", "", "", "ID", ""],
            ["fullname", "", "4", "1", "", "", "", "", "", "Full Name", ""],
            ["phone", "", "3", "1", "", "p", "", "", "", "Phone", ""],
            ["email", "", "3", "2", "", "e", "", "", "", "Email", ""],
        ];
    }

    public function testResourcesArrayExists(): void
    {
        global $RESOURCES;
        $this->assertIsArray($RESOURCES);
        $this->assertArrayHasKey('auth', $RESOURCES);
        $this->assertArrayHasKey('contacts', $RESOURCES);
    }

    public function testRightsArrayExists(): void
    {
        global $RIGHTS_1, $RIGHTS_99;
        $this->assertIsArray($RIGHTS_1);
        $this->assertIsArray($RIGHTS_99);
        $this->assertArrayHasKey('auth', $RIGHTS_1);
        $this->assertArrayHasKey('contacts', $RIGHTS_1);
    }

    public function testAuthDefinitionStructure(): void
    {
        global $auth_def;
        $this->assertIsArray($auth_def);
        $this->assertGreaterThan(0, count($auth_def));
        
        // Test first field definition structure
        $firstField = $auth_def[0];
        $this->assertIsArray($firstField);
        $this->assertEquals('id', $firstField[0]); // field name
        $this->assertEquals('ID', $firstField[9]); // display name
    }

    public function testContactsDefinitionStructure(): void
    {
        global $contacts_def;
        $this->assertIsArray($contacts_def);
        $this->assertGreaterThan(0, count($contacts_def));
        
        // Find phone field and test validation flag
        foreach ($contacts_def as $field) {
            if ($field[0] === 'phone') {
                $this->assertEquals('p', $field[5]); // phone validation flag
                break;
            }
        }
    }

    public function testEnumDefinitions(): void
    {
        global $yesno_enum, $role_enum, $vector_enum;
        
        // Test yesno enum
        $this->assertIsArray($yesno_enum);
        $this->assertArrayHasKey('0', $yesno_enum);
        $this->assertArrayHasKey('1', $yesno_enum);
        $this->assertEquals('No', $yesno_enum['0'][1]);
        $this->assertEquals('Yes', $yesno_enum['1'][1]);
        
        // Test role enum
        $this->assertIsArray($role_enum);
        $this->assertArrayHasKey('1', $role_enum);
        $this->assertEquals('Counsellor', $role_enum['1'][1]);
        
        // Test vector enum  
        $this->assertIsArray($vector_enum);
        $this->assertArrayHasKey('1', $vector_enum);
        $this->assertArrayHasKey('2', $vector_enum);
        $this->assertEquals('Inbound', $vector_enum['1'][1]);
        $this->assertEquals('Outbound', $vector_enum['2'][1]);
    }

    public function testApiDefinitions(): void
    {
        global $users_api, $contacts_api, $cases_api;
        
        // Test that API definitions exist and are arrays
        $this->assertIsArray($users_api);
        $this->assertIsArray($contacts_api);
        $this->assertIsArray($cases_api);
        
        // Test basic structure of API definitions
        $this->assertGreaterThan(0, count($users_api));
        $this->assertGreaterThan(0, count($contacts_api));
        $this->assertGreaterThan(0, count($cases_api));
    }

    public function testSubsDefinitions(): void
    {
        global $cases_subs, $activities_subs;
        
        // Test that subs definitions exist and are arrays
        $this->assertIsArray($cases_subs);
        $this->assertIsArray($activities_subs);
        
        // Test basic structure
        foreach ($cases_subs as $sub) {
            $this->assertIsArray($sub);
            $this->assertGreaterThanOrEqual(3, count($sub)); // Should have at least table, suffix, and field info
        }
    }

    public function testJoinDefinitions(): void
    {
        global $cases_join, $calls_join;
        
        // Test that join definitions exist and are arrays
        $this->assertIsArray($cases_join);
        $this->assertIsArray($calls_join);
        
        // Test join structure
        foreach ($cases_join as $joinKey => $joinDef) {
            $this->assertIsArray($joinDef);
            $this->assertEquals(3, count($joinDef)); // Should have table, alias, condition
            $this->assertIsString($joinDef[0]); // table name
            $this->assertIsString($joinDef[1]); // table alias
            $this->assertIsString($joinDef[2]); // join condition
        }
    }

    public function testCsvDefinitions(): void
    {
        global $calls_csv, $cases_csv, $clients_csv;
        
        // Test CSV field definitions
        $this->assertIsArray($calls_csv);
        $this->assertIsArray($cases_csv);
        $this->assertIsArray($clients_csv);
        
        // Test that CSV definitions contain expected fields
        $this->assertContains('id', $cases_csv);
        $this->assertContains('created_on', $cases_csv);
        $this->assertContains('uniqueid', $calls_csv);
        $this->assertContains('contact_fullname', $clients_csv);
    }

    public function testDuplicateCheckDefinitions(): void
    {
        global $addr_dup, $otp_dup, $auth_dup;
        
        // Test duplicate check definitions
        $this->assertIsArray($addr_dup);
        $this->assertIsArray($otp_dup);
        $this->assertIsArray($auth_dup);
        
        // Test structure - should have at least table, suffix, operation, field mappings
        $this->assertGreaterThanOrEqual(4, count($addr_dup));
        $this->assertEquals('addr', $addr_dup[0]); // table name
        $this->assertEquals('dup', $addr_dup[2]); // operation
    }

    public function testMetricsDefinitions(): void
    {
        global $METRICS;
        
        $this->assertIsArray($METRICS);
        $this->assertArrayHasKey('case_count', $METRICS);
        $this->assertArrayHasKey('call_count', $METRICS);
        
        // Test metric structure
        $caseCount = $METRICS['case_count'];
        $this->assertIsArray($caseCount);
        $this->assertStringContainsString('COUNT', $caseCount[0]); // Should contain COUNT function
    }
}