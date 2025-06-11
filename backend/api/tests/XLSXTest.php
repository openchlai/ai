<?php

use PHPUnit\Framework\TestCase;

require_once __DIR__ . '/../../lib/XLSX.php';

class XLSXTest extends TestCase
{
    private $xlsxGen;

    protected function setUp(): void
    {
        $this->xlsxGen = new XLSXGen();
    }

    protected function tearDown(): void
    {
        // Clean up any temporary files
        $tmpFiles = glob('/tmp/*xlsx*');
        foreach ($tmpFiles as $file) {
            if (is_file($file)) {
                unlink($file);
            }
        }
    }

    /**
     * Test constructor initializes properties correctly
     */
    public function testConstructor()
    {
        $xlsx = new XLSXGen();
        $this->assertInstanceOf(XLSXGen::class, $xlsx);
        
        // Use reflection to test private properties
        $reflection = new ReflectionClass($xlsx);
        
        $defaultFont = $reflection->getProperty('defaultFont');
        $defaultFont->setAccessible(true);
        $this->assertEquals('Calibri', $defaultFont->getValue($xlsx));
        
        $SI = $reflection->getProperty('SI');
        $SI->setAccessible(true);
        $this->assertEquals([], $SI->getValue($xlsx));
        
        $F = $reflection->getProperty('F');
        $F->setAccessible(true);
        $this->assertEquals([XLSXGen::F_NORMAL], $F->getValue($xlsx));
    }

    /**
     * Test constants are defined correctly
     */
    public function testConstants()
    {
        $this->assertEquals(0, XLSXGen::N_NORMAL);
        $this->assertEquals(1, XLSXGen::N_INT);
        $this->assertEquals(2, XLSXGen::N_DEC);
        $this->assertEquals(9, XLSXGen::N_PERCENT_INT);
        $this->assertEquals(10, XLSXGen::N_PRECENT_DEC);
        $this->assertEquals(14, XLSXGen::N_DATE);
        $this->assertEquals(20, XLSXGen::N_TIME);
        $this->assertEquals(22, XLSXGen::N_DATETIME);
        
        $this->assertEquals(0, XLSXGen::F_NORMAL);
        $this->assertEquals(1, XLSXGen::F_HYPERLINK);
        $this->assertEquals(2, XLSXGen::F_BOLD);
        $this->assertEquals(4, XLSXGen::F_ITALIC);
        $this->assertEquals(8, XLSXGen::F_UNDERLINE);
        $this->assertEquals(16, XLSXGen::F_STRIKE);
        
        $this->assertEquals(0, XLSXGen::A_DEFAULT);
        $this->assertEquals(1, XLSXGen::A_LEFT);
        $this->assertEquals(2, XLSXGen::A_RIGHT);
        $this->assertEquals(3, XLSXGen::A_CENTER);
    }

    /**
     * Test esc method escapes XML characters correctly
     */
    public function testEsc()
    {
        $this->assertEquals('&amp;', $this->xlsxGen->esc('&'));
        $this->assertEquals('&lt;', $this->xlsxGen->esc('<'));
        $this->assertEquals('&gt;', $this->xlsxGen->esc('>'));
        $this->assertEquals('', $this->xlsxGen->esc("\x00"));
        $this->assertEquals('', $this->xlsxGen->esc("\x03"));
        $this->assertEquals('', $this->xlsxGen->esc("\x0B"));
        
        // Test combination
        $this->assertEquals('&amp;&lt;&gt;test', $this->xlsxGen->esc('&<>test'));
        
        // Test normal text
        $this->assertEquals('Normal text', $this->xlsxGen->esc('Normal text'));
    }

    /**
     * Test date2excel method converts dates correctly
     */
    public function testDate2excel()
    {
        // Test basic date conversion (2000-01-01)
        $result = $this->xlsxGen->date2excel(2000, 1, 1);
        $this->assertIsFloat($result);
        $this->assertEquals(36526.0, $result);
        
        // Test with time
        $result = $this->xlsxGen->date2excel(2000, 1, 1, 12, 0, 0);
        $this->assertEquals(36526.5, $result); // 0.5 = 12 hours
        
        // Test with minutes and seconds
        $result = $this->xlsxGen->date2excel(2000, 1, 1, 6, 30, 0);
        $this->assertEquals(36526.270833333336, $result, '', 0.000001);
        
        // Test time only (year = 0)
        $result = $this->xlsxGen->date2excel(0, 0, 0, 1, 0, 0);
        $this->assertEquals(0.041666666666666664, $result, '', 0.000001);
        
        // Test 1900 leap year edge case
        $result = $this->xlsxGen->date2excel(1900, 2, 28);
        $this->assertIsFloat($result);
        
        $result = $this->xlsxGen->date2excel(1900, 3, 1);
        $this->assertIsFloat($result);
    }

    /**
     * Test num2name method converts numbers to Excel column names
     */
    public function testNum2name()
    {
        $this->assertEquals('A', $this->xlsxGen->num2name(1));
        $this->assertEquals('B', $this->xlsxGen->num2name(2));
        $this->assertEquals('Z', $this->xlsxGen->num2name(26));
        $this->assertEquals('AA', $this->xlsxGen->num2name(27));
        $this->assertEquals('AB', $this->xlsxGen->num2name(28));
        $this->assertEquals('AZ', $this->xlsxGen->num2name(52));
        $this->assertEquals('BA', $this->xlsxGen->num2name(53));
        $this->assertEquals('ZZ', $this->xlsxGen->num2name(702));
        $this->assertEquals('AAA', $this->xlsxGen->num2name(703));
    }

    /**
     * Test xlsx_val method with various value types
     */
    public function testXlsxValWithStrings()
    {
        $ct = $cv = $cs = null;
        
        // Test integer as string
        $this->xlsxGen->xlsx_val(1, '123', $ct, $cv, $cs);
        $this->assertEquals('123', $cv);
        $this->assertNull($ct);
        
        // Test zero
        $this->xlsxGen->xlsx_val(1, '0', $ct, $cv, $cs);
        $this->assertEquals('0', $cv);
        
        // Test negative integer
        $this->xlsxGen->xlsx_val(1, '-456', $ct, $cv, $cs);
        $this->assertEquals('-456', $cv);
        
        // Test large integer (should use N_INT format)
        $this->xlsxGen->xlsx_val(1, '12345678901', $ct, $cv, $cs);
        $this->assertEquals('12345678901', $cv);
        
        // Test decimal
        $this->xlsxGen->xlsx_val(1, '123.45', $ct, $cv, $cs);
        $this->assertEquals('123.45', $cv);
        
        // Test percentage integer
        $this->xlsxGen->xlsx_val(1, '50%', $ct, $cv, $cs);
        $this->assertEquals(0.5, $cv);
        
        // Test percentage decimal
        $this->xlsxGen->xlsx_val(1, '75.5%', $ct, $cv, $cs);
        $this->assertEquals(0.755, $cv);
    }

    public function testXlsxValWithDates()
    {
        $ct = $cv = $cs = null;
        
        // Test YYYY-MM-DD format
        $this->xlsxGen->xlsx_val(1, '2023-12-25', $ct, $cv, $cs);
        $this->assertIsFloat($cv);
        
        // Test DD/MM/YYYY format
        $this->xlsxGen->xlsx_val(1, '25/12/2023', $ct, $cv, $cs);
        $this->assertIsFloat($cv);
        
        // Test time HH:MM:SS
        $this->xlsxGen->xlsx_val(1, '14:30:00', $ct, $cv, $cs);
        $this->assertIsFloat($cv);
        
        // Test datetime YYYY-MM-DD HH:MM:SS
        $this->xlsxGen->xlsx_val(1, '2023-12-25 14:30:00', $ct, $cv, $cs);
        $this->assertIsFloat($cv);
        
        // Test datetime DD/MM/YYYY HH:MM:SS
        $this->xlsxGen->xlsx_val(1, '25/12/2023 14:30:00', $ct, $cv, $cs);
        $this->assertIsFloat($cv);
    }

    public function testXlsxValWithSharedStrings()
    {
        $ct = $cv = $cs = null;
        
        // Test short string (should use shared strings)
        $this->xlsxGen->xlsx_val(1, 'Hello World', $ct, $cv, $cs);
        $this->assertEquals('s', $ct);
        $this->assertEquals(0, $cv); // First shared string index
        
        // Test same string again (should reuse index)
        $this->xlsxGen->xlsx_val(1, 'Hello World', $ct, $cv, $cs);
        $this->assertEquals('s', $ct);
        $this->assertEquals(0, $cv); // Same index
        
        // Test different string
        $this->xlsxGen->xlsx_val(1, 'Another String', $ct, $cv, $cs);
        $this->assertEquals('s', $ct);
        $this->assertEquals(1, $cv); // Next index
    }

    public function testXlsxValWithLongString()
    {
        $ct = $cv = $cs = null;
        
        // Test very long string (should use inline string)
        $longString = str_repeat('A', 200);
        $this->xlsxGen->xlsx_val(1, $longString, $ct, $cv, $cs);
        $this->assertEquals('inlineStr', $ct);
        $this->assertEquals($longString, $cv);
    }

    public function testXlsxValWithNumericTypes()
    {
        $ct = $cv = $cs = null;
        
        // Test integer
        $this->xlsxGen->xlsx_val(1, 42, $ct, $cv, $cs);
        $this->assertEquals(42, $cv);
        $this->assertNull($ct);
        
        // Test float
        $this->xlsxGen->xlsx_val(1, 3.14159, $ct, $cv, $cs);
        $this->assertEquals(3.14159, $cv);
        $this->assertNull($ct);
        
        // Test negative float
        $this->xlsxGen->xlsx_val(1, -2.5, $ct, $cv, $cs);
        $this->assertEquals(-2.5, $cv);
    }

    public function testXlsxValWithDateTime()
    {
        $ct = $cv = $cs = null;
        
        $dateTime = new DateTime('2023-12-25 14:30:00');
        $this->xlsxGen->xlsx_val(1, $dateTime, $ct, $cv, $cs);
        $this->assertIsFloat($cv);
        $this->assertNull($ct);
    }

    public function testXlsxValWithInvalidInput()
    {
        $ct = $cv = $cs = null;
        
        // Test with null
        $result = $this->xlsxGen->xlsx_val(1, null, $ct, $cv, $cs);
        $this->assertNull($result);
        
        // Test with array
        $result = $this->xlsxGen->xlsx_val(1, [], $ct, $cv, $cs);
        $this->assertNull($result);
        
        // Test with object (not DateTime)
        $result = $this->xlsxGen->xlsx_val(1, new stdClass(), $ct, $cv, $cs);
        $this->assertNull($result);
    }

    /**
     * Test that COL array is updated correctly
     */
    public function testXlsxValUpdatesColumnWidths()
    {
        $reflection = new ReflectionClass($this->xlsxGen);
        $colProperty = $reflection->getProperty('COL');
        $colProperty->setAccessible(true);
        
        $ct = $cv = $cs = null;
        
        // Test that column width is tracked
        $this->xlsxGen->xlsx_val(1, 'Short', $ct, $cv, $cs);
        $cols = $colProperty->getValue($this->xlsxGen);
        $this->assertEquals(5, $cols[1]); // 'Short' has 5 characters
        
        // Test longer string in same column
        $this->xlsxGen->xlsx_val(1, 'Much longer string', $ct, $cv, $cs);
        $cols = $colProperty->getValue($this->xlsxGen);
        $this->assertEquals(18, $cols[1]); // Updated to longer length
        
        // Test shorter string doesn't reduce width
        $this->xlsxGen->xlsx_val(1, 'Hi', $ct, $cv, $cs);
        $cols = $colProperty->getValue($this->xlsxGen);
        $this->assertEquals(18, $cols[1]); // Still the max length
    }

    /**
     * Test special string patterns
     */
    public function testXlsxValSpecialPatterns()
    {
        $ct = $cv = $cs = null;
        
        // Test numeric-like string (should be right-aligned)
        $this->xlsxGen->xlsx_val(1, '123.456', $ct, $cv, $cs);
        $this->assertEquals('123.456', $cv);
        
        // Test plus prefix
        $this->xlsxGen->xlsx_val(1, '+123', $ct, $cv, $cs);
        $this->assertEquals('123', $cv); // Plus should be stripped
        
        // Test phone number pattern
        $this->xlsxGen->xlsx_val(1, '123-456-7890', $ct, $cv, $cs);
        // Should be treated as string due to pattern
    }

    /**
     * Test edge cases and boundary conditions
     */
    public function testXlsxValEdgeCases()
    {
        $ct = $cv = $cs = null;
        
        // Test empty string
        $this->xlsxGen->xlsx_val(1, '', $ct, $cv, $cs);
        $this->assertEquals('s', $ct);
        $this->assertIsInt($cv);
        
        // Test string with XML characters
        $this->xlsxGen->xlsx_val(1, '<test>&value</test>', $ct, $cv, $cs);
        $this->assertEquals('s', $ct);
        // The value should be XML-escaped when stored
        
        // Test very large number as string
        $this->xlsxGen->xlsx_val(1, '999999999999999', $ct, $cv, $cs);
        $this->assertEquals('999999999999999', $cv);
        
        // Test invalid date formats
        $this->xlsxGen->xlsx_val(1, '2023-13-32', $ct, $cv, $cs); // Invalid date
        $this->assertEquals('s', $ct); // Should be treated as string
        
        // Test invalid time format
        $this->xlsxGen->xlsx_val(1, '25:99:99', $ct, $cv, $cs); // Invalid time
        $this->assertEquals('s', $ct); // Should be treated as string
    }

    /**
     * Test shared strings functionality
     */
    public function testSharedStrings()
    {
        $reflection = new ReflectionClass($this->xlsxGen);
        $siProperty = $reflection->getProperty('SI');
        $siProperty->setAccessible(true);
        $siKeysProperty = $reflection->getProperty('SI_KEYS');
        $siKeysProperty->setAccessible(true);
        
        $ct = $cv = $cs = null;
        
        // Add first string
        $this->xlsxGen->xlsx_val(1, 'First', $ct, $cv, $cs);
        $si = $siProperty->getValue($this->xlsxGen);
        $siKeys = $siKeysProperty->getValue($this->xlsxGen);
        
        $this->assertCount(1, $si);
        $this->assertEquals('First', $si[0]);
        $this->assertArrayHasKey('~First', $siKeys);
        $this->assertEquals(0, $siKeys['~First']);
        
        // Add same string (should reuse)
        $this->xlsxGen->xlsx_val(1, 'First', $ct, $cv, $cs);
        $si = $siProperty->getValue($this->xlsxGen);
        $this->assertCount(1, $si); // Should still be 1
        $this->assertEquals(0, $cv); // Should return same index
        
        // Add different string
        $this->xlsxGen->xlsx_val(1, 'Second', $ct, $cv, $cs);
        $si = $siProperty->getValue($this->xlsxGen);
        $this->assertCount(2, $si);
        $this->assertEquals('Second', $si[1]);
        $this->assertEquals(1, $cv); // Should return new index
    }

    /**
     * Test percentage calculations
     */
    public function testPercentageCalculations()
    {
        $ct = $cv = $cs = null;
        
        // Test various percentage formats
        $testCases = [
            ['0%', 0.0],
            ['100%', 1.0],
            ['50%', 0.5],
            ['-25%', -0.25],
            ['150%', 1.5],
            ['33.33%', 0.3333],
            ['66.67%', 0.6667],
        ];
        
        foreach ($testCases as [$input, $expected]) {
            $this->xlsxGen->xlsx_val(1, $input, $ct, $cv, $cs);
            $this->assertEquals($expected, $cv, "Failed for input: $input");
        }
    }

    /**
     * Test column tracking across multiple calls
     */
    public function testColumnTracking()
    {
        $reflection = new ReflectionClass($this->xlsxGen);
        $colProperty = $reflection->getProperty('COL');
        $colProperty->setAccessible(true);
        
        $ct = $cv = $cs = null;
        
        // Test multiple columns
        $this->xlsxGen->xlsx_val(1, 'Column1', $ct, $cv, $cs);
        $this->xlsxGen->xlsx_val(2, 'Col2', $ct, $cv, $cs);
        $this->xlsxGen->xlsx_val(3, 'Column3Data', $ct, $cv, $cs);
        
        $cols = $colProperty->getValue($this->xlsxGen);
        $this->assertEquals(7, $cols[1]); // 'Column1'
        $this->assertEquals(4, $cols[2]); // 'Col2'
        $this->assertEquals(11, $cols[3]); // 'Column3Data'
    }

    /**
     * Test memory cleanup and reset functionality
     */
    public function testMemoryManagement()
    {
        $reflection = new ReflectionClass($this->xlsxGen);
        
        // Add many strings to test memory usage
        $ct = $cv = $cs = null;
        for ($i = 0; $i < 10; $i++) {
            $this->xlsxGen->xlsx_val(1, "String $i", $ct, $cv, $cs);
        }
        
        $siProperty = $reflection->getProperty('SI');
        $siProperty->setAccessible(true);
        $si = $siProperty->getValue($this->xlsxGen);
        
        // Should have at least some strings (the shared string logic may consolidate)
        $this->assertGreaterThan(0, count($si));
        $this->assertLessThanOrEqual(10, count($si));
        
        // Test that strings are being stored
        $this->assertContains('String 0', $si);
        $this->assertContains('String 1', $si);
        
        // Test duplicate string handling
        $originalCount = count($si);
        for ($i = 0; $i < 3; $i++) {
            $this->xlsxGen->xlsx_val(1, "String 0", $ct, $cv, $cs); // Repeat first string
        }
        
        $si = $siProperty->getValue($this->xlsxGen);
        $this->assertEquals($originalCount, count($si)); // Should not increase
    }
}