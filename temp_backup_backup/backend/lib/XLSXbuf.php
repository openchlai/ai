<?php

class XLSXGen 
{
	const N_NORMAL = 0; // General
	const N_INT = 1; // 0
	const N_DEC = 2; // 0.00
	const N_PERCENT_INT = 9; // 0%
	const N_PRECENT_DEC = 10; // 0.00%
	const N_DATE = 14; // mm-dd-yy
	const N_TIME = 20; // h:mm
	const N_DATETIME = 22; // m/d/yy h:mm
	
	const A_DEFAULT = 0;
	const A_LEFT = 1;
	const A_RIGHT = 2;
	const A_CENTER = 4;
	const A_TOP = 8;
	const A_MIDDLE = 16;
	const A_BOTTOM = 32;
	
	const F_NORMAL = 0;
	const F_HYPERLINK = 1;
	const F_BOLD = 2;
	const F_ITALIC = 4;
	const F_UNDERLINE = 8;
	const F_STRIKE = 16;
	
	protected $CUR_ROW;
	protected $XF, $XF_KEYS; // cellXfs
	protected $SI, $SI_KEYS; // shared strings
	
	protected $defaultFont;
	protected $defaultFontSize;

	public function __construct () 
	{
		$this->defaultFont = 'Calibri';
		 
		$this->SI = [];		// sharedStrings index
		$this->SI_KEYS = []; 	//  & keys
		
		$this->XF  = [ [self::N_NORMAL, self::A_DEFAULT, self::F_NORMAL] ]; // styles
		$this->XF_KEYS = ['N0A0F0' => 0 ];
	}
	
	public function esc ($str) 
	{
		// XML UTF-8: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
		// but we use fast version
		return str_replace( ['&', '<', '>', "\x00","\x03","\x0B"], ['&amp;', '&lt;', '&gt;', '', '', ''], $str );
	}
	
	public function date2excel ($year, $month, $day, $hours=0, $minutes=0, $seconds=0) {
	    $excelTime = (($hours * 3600) + ($minutes * 60) + $seconds) / 86400;

	    if ( $year === 0 ) {
	        return $excelTime;
        	}

		// self::CALENDAR_WINDOWS_1900
		$excel1900isLeapYear = True;
		if (((int)$year === 1900) && ($month <= 2)) { $excel1900isLeapYear = False; }
		$myExcelBaseDate = 2415020;

		//    Julian base date Adjustment
		if ($month > 2) {
			$month -= 3;
		} else {
			$month += 9;
			--$year;
		}
		//    Calculate the Julian Date, then subtract the Excel base date (JD 2415020 = 31-Dec-1899 Giving Excel Date of 0)
		$century = substr($year,0,2);
		$decade = substr($year,2,2);
		$excelDate = floor((146097 * $century) / 4) + floor((1461 * $decade) / 4) + floor((153 * $month + 2) / 5) + $day + 1721119 - $myExcelBaseDate + $excel1900isLeapYear;

		return (float) $excelDate + $excelTime;
	}
	
	function num2name ($num) 
	{
		$numeric = ($num - 1) % 26;
		$letter  = chr( 65 + $numeric );
		$num2    = (int) ( ($num-1) / 26 );
		if ( $num2 > 0 ) {
			return $this->num2name( $num2 ) . $letter;
		}
		return $letter;
	}

	function xlsx_val ($j, $v, &$ct, &$cv, &$cs)
	{
		$N = $A = $F = $FL = $C = $B = 0;
		
		// if (!isset ($this->COL[$j])) $this->COL[$j] = 0;

		if (is_string ($v)) 
		{
			$vl = mb_strlen ($v);
			if ($v==='0' || preg_match ('/^[-+]?[1-9]\d{0,14}$/', $v))  // Integer as General
			{
				$cv = ltrim( $v, '+' );
				if ( $vl > 10 ) {
					$N = self::N_INT; // [1] 0
				}
			} elseif ( preg_match( '/^[-+]?(0|[1-9]\d*)\.(\d+)$/', $v, $m ) ) {
				$cv = ltrim( $v, '+' );
				if ( strlen( $m[2] ) < 3 ) {
					$N = self::N_DEC;
				}
			} elseif ( preg_match( '/^([-+]?\d+)%$/', $v, $m ) ) {
				$cv = round( $m[1] / 100, 2 );
				$N = self::N_PERCENT_INT; // [9] 0%
			} elseif ( preg_match( '/^([-+]?\d+\.\d+)%$/', $v, $m ) ) {
				$cv = round( $m[1] / 100, 4 );
				$N = self::N_PRECENT_DEC; // [10] 0.00%
				
			} elseif ( preg_match( '/^(\d\d\d\d)-(\d\d)-(\d\d)$/', $v, $m ) ) {
				$cv = $this->date2excel( $m[1], $m[2], $m[3] );
				$N = self::N_DATE; // [14] mm-dd-yy
			} elseif ( preg_match( '/^(\d\d)\/(\d\d)\/(\d\d\d\d)$/', $v, $m ) ) {
				$cv = $this->date2excel( $m[3], $m[2], $m[1] );
				$N = self::N_DATE; // [14] mm-dd-yy
			} elseif ( preg_match( '/^(\d\d):(\d\d):(\d\d)$/', $v, $m ) ) {
				$cv = $this->date2excel( 0, 0, 0, $m[1], $m[2], $m[3] );
				$N = self::N_TIME; // time
			} elseif ( preg_match( '/^(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)$/', $v, $m ) ) {
				$cv = $this->date2excel( $m[1], $m[2], $m[3], $m[4], $m[5], $m[6] );
				$N = self::N_DATETIME; // [22] m/d/yy h:mm
			} elseif ( preg_match( '/^(\d\d)\/(\d\d)\/(\d\d\d\d) (\d\d):(\d\d):(\d\d)$/', $v, $m ) ) {
				$cv = $this->date2excel( $m[3], $m[2], $m[1], $m[4], $m[5], $m[6] );
				$N = self::N_DATETIME; // [22] m/d/yy h:mm
				
			} elseif ( preg_match( '/^[0-9+-.]+$/', $v ) ) { // Long ?
				$A = self::A_RIGHT;
			}
						
			if ( !$cv) {

				$v = $this->esc ($v); // removed tags that cn messup xlsx xml

				if ( mb_strlen ($v) > 160 ) {
					$ct = 'inlineStr';
					$cv = $v;
				} else {
					$ct = 's'; // shared string
					$cv = false;
					$skey = '~' . $v;
					if ( isset( $this->SI_KEYS[ $skey ] ) ) {
						$cv = $this->SI_KEYS[ $skey ];
					}
					if ( $cv === false ) {
						$cv = count ($this->SI);
						$this->SI_KEYS[ $skey ] = $cv;
						$this->SI[] = $v;
					}
				}
			}
					
		} elseif ( is_int( $v ) ) {
			$vl = mb_strlen( (string) $v );
			$cv = $v;
		} elseif ( is_float( $v ) ) {
			$vl = mb_strlen( (string) $v );
			$cv = $v;
		} elseif ( $v instanceof DateTime ) {
			$vl = 16;
			$cv = $this->date2excel ($v->format('Y'), $v->format('m'), $v->format('d'), $v->format('H'), $v->format('i'), $v->format('s') );
			$N = self::N_DATETIME; // [22] m/d/yy h:mm
		} else {
			return;
		}
		
		// $this->COL[$j] = max ($vl, $this->COL[$j]);

		$cs = 0;
		if ($N + $A + $F > 0 ) 
		{
			$NAF = 'N' . $N . 'A' . $A . 'F' . $F;
			if ( isset( $this->XF_KEYS[ $NAF ] ) ) {
				$cs = $this->XF_KEYS[ $NAF ];
			}
			if ( $cs === 0 ) {
				$cs = count( $this->XF );
				$this->XF_KEYS[ $NAF ] = $cs;
				$this->XF[] = [$N, $A, $F];
			}
		}
	}

	function _xlsx_cols_k ($u, $fd, &$ja)
	{
		$a = $GLOBALS[($u."_def")];
	        $kk = $GLOBALS[($u."_k")];
	        $jj = null;
	        $jn = count ($a);
		if (isset ($GLOBALS[($u."_csv")])) { $jj = $GLOBALS[($u."_csv")]; $jn = count ($jj); }
		for ($j=0; $j<$jn; $j++)
        	{
			$j_=$j;
			if ($jj!=null) $j_ = $kk[$jj[$j]];
        	        $v = strtoupper ($a[$j_][9]);
        	        $cname = $this->num2name (($j+1+$ja)) . 1;
        	        $ct = $cv = null;
			$cs = 0;
			$this->xlsx_val (($j+1+$ja), $v, $ct, $cv, $cs);
			$s = '<c r="' . $cname . '"'.($ct ? ' t="'.$ct.'"' : '').($cs ? ' s="'.$cs.'"' : '').'>'
				.($ct === 'inlineStr' ? '<is><t>'.$cv.'</t></is>' : '<v>' . $cv . '</v>')."</c>\r\n";	
			fwrite ($fd, $s);
		}
		$ja += $jn;
	}
	
	function _xlsx_cols_v ($u, $fd, &$ja, $row, $start)
	{
		$a = $GLOBALS[($u."_def")];
	        $kk = $GLOBALS[($u."_k")];
	        $jj = null;
	        $jn = count ($a);
		if (isset ($GLOBALS[($u."_csv")])) {  $jj = $GLOBALS[($u."_csv")]; $jn = count ($jj); }
		for ($j=0; $j<$jn; $j++)
        	{
			$j_=$j;
			if ($jj!=null) $j_ = $kk[$jj[$j]];
			$v = $row[($j_+$start)];
			$v = str_replace (['^'], [''], $v);
			if ($a[$j_][3]==3 && strlen ($v)>0) { $v = _date ($a[$j_][10], $v); }
			if ($a[$j_][3]==2 && strlen($a[$j_][10])>0) { $v = _enum ($a[$j_][10], $v); }
			$cname = $this->num2name (($j+1+$ja)) . $this->CUR_ROW;
        	        $ct = $cv = null;
			$cs = 0;
			$this->xlsx_val (($j+1+$ja), $v, $ct, $cv, $cs);
			// error_log ("[xlsx_val] ".$j.") ".$a[$j_][0]."=".$v."|".$ct."|".$cv);
			$s = '<c r="' . $cname . '"'.($ct ? ' t="'.$ct.'"' : '').($cs ? ' s="'.$cs.'"' : '').'>'
				.($ct === 'inlineStr' ? '<is><t>'.$cv.'</t></is>' : '<v>' . $cv . '</v>')."</c>\r\n";
			fwrite ($fd, $s);
		}
		$ja += $jn;		
		return count ($a);
	}

	function xlsx_sheet ($u, $res, $fd, $join)
	{
		$this->COL = [];
		$this->CUR_ROW = 1;
		
		$nj = 0;
		$uj = null;
		if (isset ($GLOBALS[($u."_join")])) { $nj=count ($join);  $uj=$GLOBALS[($u."_join")]; }
		
		$s = '<row r="'.$this->CUR_ROW.'">';
		fwrite ($fd, $s);
		$ja = 0;
		$this->_xlsx_cols_k ($u, $fd, $ja);
		for ($i=0; $i<$nj; $i++)
		{
			if (!isset ($uj[$join[$i]])) continue;
			$this->_xlsx_cols_k ($uj[$join[$i]][0], $fd, $ja);
		}
		$s = "</row>\r\n";
		fwrite ($fd, $s);
		
		while (($row = mysqli_fetch_row ($res)))
        	{
        		$this->CUR_ROW++;
			$s = '<row r="'.$this->CUR_ROW.'">';
			fwrite ($fd, $s);
        		$ja = 0;
        		$start = $this->_xlsx_cols_v ($u, $fd, $ja, $row, 0);
			for ($i=0; $i<$nj; $i++)
			{
				if (!isset ($uj[$join[$i]])) continue;
				$start += $this->_xlsx_cols_v ($uj[$join[$i]][0], $fd, $ja, $row, $start);
			}
                	$s = "</row>\r\n";
			fwrite ($fd, $s);
        	}
	}

	function xlsx_data ($fz, $data, $fb)
	{
		if ($fb!=null) 
		{
			fseek ($fb, 0);
			return stream_copy_to_stream ($fb, $fz); // {ROWS}
		}
		return fwrite ($fz, $data);
	}
	
	function xlsx_data_len ($data, $fb)
	{
		if ($fb!=null) return ftell ($fb);
		return mb_strlen($data, '8bit');
	}
	
	function xlsx_crc32 ($data, $fb) 
	{
		if ($fb!=null) 
		{
			$ctx = hash_init ('crc32b');
			fseek ($fb, 0);
			hash_update_stream($ctx, $fb);
			$v = hexdec (hash_final ($ctx));
			//$data = stream_get_contents ($fb, null, 0); // verify hash_stream return same as string one
			//$v_ = crc32 ($data);
			// error_log (" CRC32 Stream: ".$v."|".$v_." | ".ftell ($fb)."|");
			return $v;
		}
		$v = crc32 ($data);
		// error_log (" CRC32 String: ".$v." | ".strlen ($data));
		return $v;
	}
	
	function xlsx_bin_write ($fz, &$cdrec, $cfilename, $data, $fb=null) 
	{
		$zipSignature = "\x50\x4b\x03\x04"; // local file header signature
		$dirSignature = "\x50\x4b\x01\x02"; // central dir header signature
		
		// Convert date and time to DOS Format, and set then
	        $lastmod_timeS  = str_pad(decbin(date('s')>=32?date('s')-32:date('s')), 5, '0', STR_PAD_LEFT);
        	$lastmod_timeM  = str_pad(decbin(date('i')), 6, '0', STR_PAD_LEFT);
        	$lastmod_timeH  = str_pad(decbin(date('H')), 5, '0', STR_PAD_LEFT);
        	$lastmod_dateD  = str_pad(decbin(date('d')), 5, '0', STR_PAD_LEFT);
        	$lastmod_dateM  = str_pad(decbin(date('m')), 4, '0', STR_PAD_LEFT);
        	$lastmod_dateY  = str_pad(decbin(date('Y')-1980), 7, '0', STR_PAD_LEFT);

		$e = [];
		$e['uncsize'] = $this->xlsx_data_len ($data, $fb);
		$e['comsize'] = $e['uncsize']; // nb: no compression applied
		$e['vneeded'] = 10;
		$e['cmethod'] = 0;
		$e['bitflag'] = 0;
		$e['crc_32']  = $this->xlsx_crc32 ($data, $fb);
        	$e['moddate'] = 21708; // bindec("$lastmod_dateY$lastmod_dateM$lastmod_dateD");
		$e['modtime'] = 26710; // bindec("$lastmod_timeH$lastmod_timeM$lastmod_timeS");
        	$e['offset'] = ftell ($fz);
        	
        	// $v_1 = pack ('v',10);
        	// $v_2 = pack ('s',10);
        	// error_log ("pack". $v_1." ".$v_2);
        	
		fwrite($fz, $zipSignature);
		fwrite($fz, pack('s', $e['vneeded'])); // version_needed
		fwrite($fz, pack('s', $e['bitflag'])); // general_bit_flag
		fwrite($fz, pack('s', $e['cmethod'])); // compression_method
		fwrite($fz, pack('s', $e['modtime'])); // lastmod_time
		fwrite($fz, pack('s', $e['moddate'])); // lastmod_date
		fwrite($fz, pack('V', $e['crc_32']));  // crc-32
		fwrite($fz, pack('I', $e['comsize'])); // compressed_size
		fwrite($fz, pack('I', $e['uncsize'])); // uncompressed_size
		fwrite($fz, pack('s', mb_strlen($cfilename, '8bit')));   // file_name_length
		fwrite($fz, pack('s', 0));  // extra_field_length
		fwrite($fz, $cfilename);    // file_name
	        // ignoring extra_field
		$this->xlsx_data ($fz, $data, $fb);

		// Append it to central dir
		$e['external_attributes']  = 32; // (substr($cfilename, -1) === '/'&&!$zdata)?16:32; // Directory or file name
	        $e['comments']             = '';

		$cdrec .= $dirSignature;
	        $cdrec .= "\x0\x0";                  // version made by
		$cdrec .= pack('v', $e['vneeded']); // version needed to extract
		$cdrec .= "\x0\x0";                  // general bit flag
		$cdrec .= pack('v', $e['cmethod']); // compression method
		$cdrec .= pack('v', $e['modtime']); // lastmod time
		$cdrec .= pack('v', $e['moddate']); // lastmod date
		$cdrec .= pack('V', $e['crc_32']);  // crc32
		$cdrec .= pack('V', $e['comsize']); // compressed filesize
		$cdrec .= pack('V', $e['uncsize']); // uncompressed filesize
		$cdrec .= pack('v', mb_strlen($cfilename,'8bit')); // file name length
		$cdrec .= pack('v', 0);                // extra field length
		$cdrec .= pack('v', mb_strlen($e['comments'],'8bit')); // file comment length
		$cdrec .= pack('v', 0); // disk number start
		$cdrec .= pack('v', 0); // internal file attributes
		$cdrec .= pack('V', $e['external_attributes']); // internal file attributes
		$cdrec .= pack('V', $e['offset']); // relative offset of local header
		$cdrec .= $cfilename;
		$cdrec .= $e['comments'];
		
		return 1;
	}
    
	function xlsx_gen ($u, $res, $join, &$fz)
	{
		$doc_ts = date ('Y-m-d\TH:i:s');	        
	        $cdrec = "";
	        $entries = 0;
	        
	        // $s="Test Content";
	        // $entries += $this->xlsx_bin_write ($fz, $cdrec, "[Content_Types].xml", $s);
	        
	        $fb_ = fopen ('php://temp','rwb'); // "xl/worksheets/sheet1.xml"
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" 
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">';
		// $s .= '<sheetFormatPr customHeight="1" defaultColWidth="14.43" defaultRowHeight="15.0"/>';
		$s .= '<sheetData>';
		//$s .= '<row r="1" ht="33.75" customHeight="1"/>'; // title
		//$s .= '<row r="2" ht="173.25" customHeight="1"/>'; // chart space
		fwrite ($fb_, $s);
		$this->xlsx_sheet ($u, $res, $fb_, $join);
		fwrite ($fb_, '</sheetData>');
		//fwrite ($fb_, '<drawing r:id="rId1"/>'); // sample drawing
		//{HYPERLINKS}
		fwrite ($fb_, '</worksheet>');
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/worksheets/sheet1.xml", null, $fb_);
		fclose ($fb_);
		
		
	        $s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">

<Default ContentType="application/xml" Extension="xml"/>
<Default ContentType="image/png" Extension="png"/>
<Default ContentType="application/vnd.openxmlformats-package.relationships+xml" Extension="rels"/>

<Override ContentType="application/vnd.openxmlformats-package.core-properties+xml" PartName="/docProps/core.xml"/>

<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml" PartName="/xl/workbook.xml"/>

<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml" PartName="/xl/styles.xml"/>
<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml" PartName="/xl/sharedStrings.xml"/>

<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml" PartName="/xl/worksheets/sheet1.xml"/>
<Override ContentType="application/vnd.openxmlformats-officedocument.drawing+xml" PartName="/xl/drawings/drawing1.xml"/>

</Types>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "[Content_Types].xml", $s);
		
		
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "_rels/.rels", $s);


		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dcterms:created xsi:type="dcterms:W3CDTF">'.$doc_ts.'</dcterms:created></cp:coreProperties>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "docProps/core.xml", $s);
	
	
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
</Relationships>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/_rels/workbook.xml.rels", $s);
		

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<fileVersion appName="VoiceApps"/>
<sheets>
<sheet name="Sheet1" sheetId="1" state="visible" r:id="rId1"/>
</sheets>
</workbook>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/workbook.xml", $s);


		
		
		error_log (json_encode ($this->XF_KEYS));
		

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
		$s .= '<fonts count="'.count($this->XF).'">';
		foreach ( $this->XF as $xf ) 
		{
			$s .= '<font><name val="'.$this->defaultFont.'"/>';
			//if ($this->defaultFontSize) $s .= '<sz val="'.$this->defaultFontSize.'"/>';
			//if ($xf[2] & self::F_BOLD) $s .= '<b/>';
			//if ($xf[2] & self::F_ITALIC) $s .= '<i/>';
			//if ($xf[2] & self::F_UNDERLINE) $s .= '<u/>';
			//if ($xf[2] & self::F_STRIKE) $s .= '<strike/>';
			//if ($xf[2] & self::F_HYPERLINK) $s .= '<u/>';
			//if ($xf[2] & self::F_COLOR) $s .= '<color rgb="'.$xf[4].'"/>';
			$s .= '</font>';
		}
		$s .= '</fonts>';				
		$s .= '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>';
		$s .= '<borders count="1"><border></border></borders>';
		$s .= '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" /></cellStyleXfs>';
		$s .= '<cellXfs count="'.count($this->XF).'">';
		foreach ( $this->XF as $xf ) 
		{
			$align = ($xf[1] & self::A_LEFT ? ' horizontal="left"' : '')
                        .($xf[1] & self::A_RIGHT ? ' horizontal="right"' : '')
                        .($xf[1] & self::A_CENTER ? ' horizontal="center"' : '')
                        .($xf[1] & self::A_TOP ? ' vertical="top"' : '')
                        .($xf[1] & self::A_MIDDLE ? ' vertical="center"' : '')
                        .($xf[1] & self::A_BOTTOM ? ' vertical="bottom"' : '');

			$s .= '<xf numFmtId="'.$xf[0].'" fontId="0" fillId="0" borderId="0" xfId="0"'
                        .($xf[0] > 0 ? ' applyNumberFormat="1"' : '')
                       // .($F_ID > 0 ? ' applyFont="1"' : '')
                       // .($FL_ID > 0 ? ' applyFill="1"' : '')
                        .($align ? ' applyAlignment="1"><alignment'.$align . '/></xf>' : '/>');
		}
		$s .= '</cellXfs>';
		$s .= '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/styles.xml", $s);


		$fb_ = fopen('php://temp','rwb'); // "xl/sharedStrings.xml"
		if (!count($this->SI)) $this->SI[] = 'No Data';
		$si_cnt = count ($this->SI);
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="'.$si_cnt.'" uniqueCount="'.$si_cnt.'">';
		fwrite ($fb_, $s);
		for ($i=0; $i<$si_cnt; $i++)
		{
			$s = '<si><t>'.$this->SI[$i] ."</t></si>\r\n";
			fwrite ($fb_, $s);
		}
		fwrite ($fb_, '</sst>');
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/sharedStrings.xml", null, $fb_);
		fclose ($fb_);	

		
		// --------------
		
		/* $s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/>
</Relationships>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/worksheets/_rels/sheet1.xml.rels", $s);
		
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>
</Relationships>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/drawings/_rels/drawing1.xml.rels", $s);
		
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xdr:wsDr 
xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" 
xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" 
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" 
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram">
<xdr:oneCellAnchor>
<xdr:from> <xdr:col>0</xdr:col> <xdr:colOff>400050</xdr:colOff> <xdr:row>1</xdr:row> <xdr:rowOff>219075</xdr:rowOff> </xdr:from>
<xdr:ext cx="13030200" cy="1743075"/>
<xdr:pic> 
<xdr:nvPicPr> <xdr:cNvPr id="0" name="image1.png" title="Image"/> <xdr:cNvPicPr preferRelativeResize="0"/> </xdr:nvPicPr>
<xdr:blipFill> <a:blip cstate="print" r:embed="rId1"/> <a:stretch><a:fillRect/></a:stretch></xdr:blipFill>
<xdr:spPr> <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/> </xdr:spPr>
</xdr:pic>
<xdr:clientData fLocksWithSheet="0"/>
</xdr:oneCellAnchor>
</xdr:wsDr>';
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/drawings/drawing1.xml", $s);
		
		$fb_ = fopen ('/var/www/html/helpline/images/canvas.png','rb'); 
		fseek ($fb_, 0, SEEK_END);
		error_log (" FB ".ftell ($fb_));
		$entries += $this->xlsx_bin_write ($fz, $cdrec, "xl/media/image1.png", null, $fb_);
		fclose ($fb_);	
		*/
		
		// --------------
		
		$dirSignatureE= "\x50\x4b\x05\x06"; // end of central dir signature
	        $zipComments = 'Generated by Voiceapps';
		$before_cd = ftell ($fz);

		fwrite ($fz, $cdrec);
		// end of central dir
		fwrite ($fz, $dirSignatureE);
		fwrite ($fz, pack('v', 0)); // number of this disk
		fwrite ($fz, pack('v', 0)); // number of the disk with the start of the central directory
		fwrite ($fz, pack('v', $entries)); // total # of entries "on this disk"
		fwrite ($fz, pack('v', $entries)); // total # of entries overall
		fwrite ($fz, pack('V', mb_strlen ($cdrec,'8bit')));     // size of central dir
		fwrite ($fz, pack('V', $before_cd));         // offset to start of central dir
		fwrite ($fz, pack('v', mb_strlen($zipComments,'8bit'))); // .zip file comment length
		fwrite ($fz, $zipComments);
	}
}

function _xlsx_download ($u, $res, $join)
{
	$fz = fopen ('php://temp','wb');
	if (!$fz) return false;
	$x = new XLSXGen();
	$x->xlsx_gen ($u, $res, $join, $fz);
	
	//$crc_ = crc32 ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
	//error_log ("CRC: ".$crc_);
	
	$file_name = $u."_".date ('D, d M Y H:i:s' , time()).".xlsx";
	$file_size = ftell ($fz);
	header('Content-type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
	header('Content-Disposition: attachment; filename="'.$file_name.'"');
	header('Last-Modified: ' . date('D, d M Y H:i:s' , time() ));
	header('Content-Length: '.$file_size);
	header('Cache-Control: no-cache');
        header("Content-Transfer-Encoding: binary");
        while( ob_get_level() ) {
            ob_end_clean();
        }
        fseek ($fz, 0);
        fpassthru ($fz);
       	exit (0);
}

?>
