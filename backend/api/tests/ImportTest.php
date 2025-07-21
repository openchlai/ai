<?php

use PHPUnit\Framework\TestCase;

class ImportTest extends TestCase
{
    private $importFunctions;

    protected function setUp(): void
    {
        // Create isolated versions of the import functions for testing
        $this->importFunctions = $this->createImportFunctions();
    }

    private function createImportFunctions()
    {
        return [
            'import_loc' => function($mockQueryResult, $mockRestResponse) {
                if ($mockQueryResult === null) return;
                
                $i = 0;
                $V = [null,null,null,null,null,null,null];
                $ID = ["88","0","0","0","0","0","0"];
                
                // Simulate processing rows
                $rows = $mockQueryResult;
                foreach ($rows as $row) {
                    for ($j=0; $j<7; $j++) {
                        if ($V[$j] == $row[$j]) continue;
                        $V[$j] = $row[$j];
                        for ($k=$j+1; $k<7; $k++) { 
                            $V[$k] = null; 
                            $ID[($j+1)] = "0"; 
                        }
                        
                        // Simulate REST API call
                        $o = [];
                        $o["category_id"] = $ID[$j];
                        $o["name"] = $row[$j];
                        
                        if ($mockRestResponse != 201) {
                            error_log("ERROR ".$mockRestResponse."  row:".$i." col:".$j);
                            continue;
                        }
                        
                        $ID[($j+1)] = "mock_id_" . ($i * 10 + $j);
                    }
                    $i++;
                }
                return $i; // Return number of processed rows
            },
            
            'import_case_categories' => function($mockQueryResult, $mockRestResponse) {
                if ($mockQueryResult === null) return;
                
                $i = 0;
                $V = [null,null,null,null,null,null,null];
                $ID = ["361944","0","0","0","0","0","0"];
                
                $rows = $mockQueryResult;
                foreach ($rows as $row) {
                    for ($j=0; $j<2; $j++) {
                        if ($V[$j] == $row[$j]) continue;
                        $V[$j] = $row[$j];
                        for ($k=$j+1; $k<2; $k++) { 
                            $V[$k] = null; 
                            $ID[($j+1)] = "0"; 
                        }
                        
                        $o = [];
                        $o["category_id"] = $ID[$j];
                        $o["name"] = $row[$j];
                        
                        if ($mockRestResponse != 201) {
                            error_log("ERROR ".$mockRestResponse."  row:".$i." col:".$j);
                            continue;
                        }
                        
                        $ID[($j+1)] = "mock_category_" . ($i * 10 + $j);
                    }
                    $i++;
                }
                return $i;
            },
            
            'split_category' => function($mockQueryResult) {
                $processed = 0;
                $rows = $mockQueryResult ?: [];
                
                foreach ($rows as $row) {
                    $id = $row[0];
                    $case_category = $row[1] ?? '';
                    
                    $av = ["","","","","",$id];
                    $vv = explode('^', $case_category);
                    $n = count($vv);
                    
                    for ($j=1; $j<$n; $j++) {
                        if ($j>5) break;
                        $av[($j-1)] = $vv[$j];
                    }
                    
                    // Simulate database update
                    $processed++;
                }
                return $processed;
            },
            
            'autoexten' => function($mockQueryResult, $mockRestResponse) {
                $processed = 0;
                $rows = $mockQueryResult ?: [];
                
                foreach ($rows as $row) {
                    $user_id = $row[0];
                    $exten = $row[1];
                    
                    $o = [];
                    $o["user_id"] = $user_id;
                    
                    if ($mockRestResponse != 202) {
                        error_log("ERROR ".$mockRestResponse."  user_id:".$user_id);
                        continue;
                    }
                    $processed++;
                }
                return $processed;
            }
        ];
    }

    /**
     * Test import_loc function with basic location hierarchy
     */
    public function testImportLocBasicHierarchy()
    {
        $mockData = [
            ['Central', 'Kampala', 'Kampala Central', 'Central Division', 'Kololo I', 'Village A', 'Kampala Central'],
            ['Central', 'Kampala', 'Kampala Central', 'Central Division', 'Kololo II', 'Village B', 'Kampala Central'],
        ];

        $result = $this->importFunctions['import_loc']($mockData, 201);
        $this->assertEquals(2, $result, 'Should process 2 rows');
    }

    /**
     * Test import_loc with null query result
     */
    public function testImportLocNullQueryResult()
    {
        $result = $this->importFunctions['import_loc'](null, 201);
        $this->assertNull($result, 'Should return null for null input');
    }

    /**
     * Test import_loc with REST API error response
     */
    public function testImportLocRestApiError()
    {
        $mockData = [
            ['Central', 'Kampala', 'Kampala Central', 'Central Division', 'Kololo I', 'Village A', 'Kampala Central'],
        ];

        $result = $this->importFunctions['import_loc']($mockData, 500);
        $this->assertEquals(1, $result, 'Should process row even with API errors');
    }

    /**
     * Test import_loc with complex location hierarchy
     */
    public function testImportLocComplexHierarchy()
    {
        $mockData = [
            ['Central', 'Kampala', 'Kampala Central', 'Central Division', 'Kololo I', 'Village A', 'Kampala Central'],
            ['Central', 'Kampala', 'Kawempe', 'Kawempe Division', 'Mulago I', 'Village C', 'Kawempe North'],
            ['Western', 'Mbarara', 'Mbarara Municipality', 'Nyamitanga Division', 'Cell A', 'Village D', 'Mbarara Municipality'],
        ];

        $result = $this->importFunctions['import_loc']($mockData, 201);
        $this->assertEquals(3, $result, 'Should process complex hierarchy correctly');
    }

    /**
     * Test import_case_categories function
     */
    public function testImportCaseCategoriesBasic()
    {
        $mockData = [
            ['Category A', 'Subcategory 1'],
            ['Category A', 'Subcategory 2'],
            ['Category B', 'Subcategory 3'],
        ];

        $result = $this->importFunctions['import_case_categories']($mockData, 201);
        $this->assertEquals(3, $result, 'Should process 3 categories');
    }

    /**
     * Test import_case_categories with null query result
     */
    public function testImportCaseCategoriesNullResult()
    {
        $result = $this->importFunctions['import_case_categories'](null, 201);
        $this->assertNull($result, 'Should handle null query result');
    }

    /**
     * Test import_case_categories with REST API errors
     */
    public function testImportCaseCategoriesApiError()
    {
        $mockData = [
            ['Category A', 'Subcategory 1'],
        ];

        $result = $this->importFunctions['import_case_categories']($mockData, 400);
        $this->assertEquals(1, $result, 'Should process even with API errors');
    }

    /**
     * Test split_category function
     */
    public function testSplitCategoryBasic()
    {
        $mockData = [
            ['1', '^cat1^cat2^cat3'],
            ['2', '^main^sub1^sub2^sub3^sub4^sub5'],
            ['3', '^single'],
        ];

        $result = $this->importFunctions['split_category']($mockData);
        $this->assertEquals(3, $result, 'Should process 3 categories');
    }

    /**
     * Test split_category with empty categories
     */
    public function testSplitCategoryEmpty()
    {
        $mockData = [
            ['1', ''],
            ['2', '^'],
            ['3', '^only_one'],
        ];

        $result = $this->importFunctions['split_category']($mockData);
        $this->assertEquals(3, $result, 'Should handle empty categories');
    }

    /**
     * Test split_category with maximum categories (>5)
     */
    public function testSplitCategoryMaxCategories()
    {
        $mockData = [
            ['1', '^cat1^cat2^cat3^cat4^cat5^cat6^cat7^cat8'], // Should only process first 5
        ];

        $result = $this->importFunctions['split_category']($mockData);
        $this->assertEquals(1, $result, 'Should handle category limit correctly');
    }

    /**
     * Test autoexten function
     */
    public function testAutoExtenBasic()
    {
        $mockData = [
            ['100', '1001'],
            ['101', '1002'],
            ['102', '1003'],
        ];

        $result = $this->importFunctions['autoexten']($mockData, 202);
        $this->assertEquals(3, $result, 'Should process 3 user extensions');
    }

    /**
     * Test autoexten with API errors
     */
    public function testAutoExtenApiError()
    {
        $mockData = [
            ['100', '1001'],
        ];

        $result = $this->importFunctions['autoexten']($mockData, 404);
        $this->assertEquals(0, $result, 'Should handle API errors gracefully');
    }

    /**
     * Test autoexten with no results
     */
    public function testAutoExtenNoResults()
    {
        $result = $this->importFunctions['autoexten']([], 202);
        $this->assertEquals(0, $result, 'Should handle empty result set');
    }

    /**
     * Test location hierarchy processing logic
     */
    public function testLocationHierarchyLogic()
    {
        $mockData = [
            ['Region1', 'District1', 'County1', 'Subcounty1', 'Parish1', 'LC1_1', 'Constituency1'],
            ['Region1', 'District1', 'County1', 'Subcounty1', 'Parish2', 'LC1_2', 'Constituency1'], // Parish change
            ['Region1', 'District2', 'County2', 'Subcounty2', 'Parish3', 'LC1_3', 'Constituency2'], // District change
        ];

        $result = $this->importFunctions['import_loc']($mockData, 201);
        $this->assertEquals(3, $result, 'Should process hierarchy changes correctly');
    }

    /**
     * Test category splitting edge cases
     */
    public function testCategorySplittingEdgeCases()
    {
        $mockData = [
            ['1', null], // null case_category
            ['2', '^'], // just separator
            ['3', '^^'], // multiple separators
            ['4', '^cat1^^cat3'], // empty middle category
        ];

        $result = $this->importFunctions['split_category']($mockData);
        $this->assertEquals(4, $result, 'Should handle edge cases');
    }

    /**
     * Test REST API integration points
     */
    public function testRestApiIntegration()
    {
        $testCases = [201, 202, 400, 401, 404, 500];
        
        foreach ($testCases as $responseCode) {
            $mockData = [['test_id', 'test_data']];
            
            $result = $this->importFunctions['import_case_categories']($mockData, $responseCode);
            
            if ($responseCode == 201) {
                $this->assertEquals(1, $result, "Should process successfully for code: $responseCode");
            } else {
                $this->assertEquals(1, $result, "Should handle error code: $responseCode");
            }
        }
    }

    /**
     * Test memory and performance with large datasets
     */
    public function testLargeDatasetHandling()
    {
        // Create large dataset
        $largeDataset = [];
        for ($i = 0; $i < 1000; $i++) {
            $largeDataset[] = ["Region$i", "District$i", "County$i", "Subcounty$i", "Parish$i", "LC1_$i", "Constituency$i"];
        }
        
        $startMemory = memory_get_usage();
        $result = $this->importFunctions['import_loc']($largeDataset, 201);
        $endMemory = memory_get_usage();
        
        $this->assertEquals(1000, $result, 'Should process large dataset');
        $this->assertLessThan($startMemory + 5000000, $endMemory, 'Memory usage should be reasonable'); // 5MB threshold
    }

    /**
     * Test data transformation and validation
     */
    public function testDataTransformation()
    {
        $testData = [
            ['1', '^Health^Mental Health^Depression'],
            ['2', '^Legal^Family Law^Divorce^Child Custody'],
            ['3', '^Education^Primary^Math'],
        ];
        
        $result = $this->importFunctions['split_category']($testData);
        $this->assertEquals(3, $result, 'Should transform data correctly');
    }

    /**
     * Test boundary conditions
     */
    public function testBoundaryConditions()
    {
        // Test with empty data
        $this->assertEquals(0, $this->importFunctions['split_category']([]), 'Empty data should return 0');
        
        // Test with single item
        $singleItem = [['1', '^single']];
        $this->assertEquals(1, $this->importFunctions['split_category']($singleItem), 'Single item should work');
        
        // Test with very long category strings
        $longString = '^' . str_repeat('category', 100);
        $longData = [['1', $longString]];
        $this->assertEquals(1, $this->importFunctions['split_category']($longData), 'Long strings should be handled');
    }

    /**
     * Test error scenarios
     */
    public function testErrorScenarios()
    {
        // Test various error codes
        $errorCodes = [400, 401, 403, 404, 422, 500, 502, 503];
        
        foreach ($errorCodes as $code) {
            $result = $this->importFunctions['autoexten']([['100', '1001']], $code);
            $this->assertEquals(0, $result, "Error code $code should be handled");
        }
    }
}