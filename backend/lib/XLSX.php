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
	const F_NORMAL = 0;
	const F_HYPERLINK = 1;
	const F_BOLD = 2;
	const F_ITALIC = 4;
	const F_UNDERLINE = 8;
	const F_STRIKE = 16;
	const A_DEFAULT = 0;
	const A_LEFT = 1;
	const A_RIGHT = 2;
	const A_CENTER = 3;
	
	protected $defaultFont;
	protected $COL;
	protected $F, $F_KEYS; // fonts
	protected $XF, $XF_KEYS; // cellXfs
	protected $SI, $SI_KEYS; // shared strings
	protected $CUR_ROW;
	
	public function __construct() 
	{
		$this->defaultFont = 'Calibri';
	
		$this->SI = [];		// sharedStrings index
		$this->SI_KEYS = []; //  & keys
		
		$this->F = [ self::F_NORMAL ]; // fonts
		$this->F_KEYS = [0]; // & keys
		
		$this->XF  = [ [self::N_NORMAL, self::F_NORMAL, self::A_DEFAULT] ]; // styles
		$this->XF_KEYS = ['N0F0A0' => 0 ]; // & keys
	}
	
	public function esc( $str ) {
		// XML UTF-8: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
		// but we use fast version
		return str_replace( ['&', '<', '>', "\x00","\x03","\x0B"], ['&amp;', '&lt;', '&gt;', '', '', ''], $str );
	}
	
	public function date2excel($year, $month, $day, $hours=0, $minutes=0, $seconds=0) {
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
	
	function num2name($num) 
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
		$N = $F = $A = 0;
		
		if (!isset ($this->COL[$j])) $this->COL[$j] = 0;

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

				$v = $this->esc ($v);

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
						$this->SI[] = $v;
						$cv = count( $this->SI ) - 1;
						$this->SI_KEYS[ $skey ] = $cv;
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
		
		$this->COL[$j] = max ($vl, $this->COL[$j]);

		$cs = 0;
		/*if ($N + $F + $A > 0 ) 
		{
			if ( isset($this->F_KEYS[ $F ] ) ) {
				$cf = $this->F_KEYS[ $F ];
			} else {
				$cf = count($this->F);
				$this->F_KEYS[$F] = $cf;
				$this->F[] = $F;
			}
			$NFA = 'N' . $N . 'F' . $cf . 'A' . $A;
			if ( isset( $this->XF_KEYS[ $NFA ] ) ) {
				$cs = $this->XF_KEYS[ $NFA ];
			}
			if ( $cs === 0 ) {
				$cs = count( $this->XF );
				$this->XF_KEYS[ $NFA ] = $cs;
				$this->XF[] = [$N, $cf, $A];
			}
		}*/
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

	function xlsx_sheet ($u, $res, $fd, $join)
	{
		$this->COL = [];
		$this->CUR_ROW = 1;
		
		$nj = 0;
		$uj = null;
		if (isset ($GLOBALS[($u."_join")])) { $nj=count ($join);  $uj=$GLOBALS[($u."_join")]; }
		
		$s = '<row r="1">';
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


	function xlsx_gen ($u, $res, $join)
	{
		$doc_ts = date ('Y-m-d\TH:i:s');
		$tmp = "/tmp/".$doc_ts.microtime('float')._rands (16,'alpha');
		$dirs = ["_rels", "docProps", "xl", "xl/_rels", "xl/worksheets"];
		$files = ["_rels/.rels", "docProps/core.xml", "docProps/app.xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels", "[Content_Types].xml", "xl/styles.xml", "xl/sharedStrings.xml", "xl/worksheets/sheet1.xml"];
		
		mkdir ($tmp);
		foreach ($dirs as $dir) mkdir ($tmp."/".$dir);

		$fd_sheet = fopen ($tmp.'/_sheet1_', 'w+');
		$this->xlsx_sheet ($u, $res, $fd_sheet, $join);
		
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>';
		file_put_contents (($tmp."/_rels/.rels"), $s);


		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dcterms:created xsi:type="dcterms:W3CDTF">'.$doc_ts.'</dcterms:created>
<dc:language>en-US</dc:language>
<dcterms:modified xsi:type="dcterms:W3CDTF">'.$doc_ts.'</dcterms:modified>
<cp:revision>1</cp:revision>
</cp:coreProperties>';
		file_put_contents (($tmp."/docProps/core.xml"), $s);

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<TotalTime>0</TotalTime>
<Application>SimpleXLSXGEn</Application></Properties>';
		file_put_contents (($tmp."/docProps/app.xml"), $s);

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<fileVersion appName="SimpleXLSXGen"/><sheets>
<sheet name="Sheet1" sheetId="1" state="visible" r:id="rId2"/>
</sheets></workbook>';
		file_put_contents (($tmp."/xl/workbook.xml"), $s);

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>';
		file_put_contents (($tmp."/xl/_rels/workbook.xml.rels"), $s);

		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Override PartName="/rels/.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/xl/_rels/workbook.xml.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/_rels/.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>';
		file_put_contents (($tmp."/[Content_Types].xml"), $s);


		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
		$s .= '<fonts count="'.count($this->F).'">';
		foreach ( $this->F as $f ) 
		{
			$s .= '<font><name val="'.$this->defaultFont.'"/><family val="2"/>';
			// $s .= '<sz val="'.$this->defaultFontSize.'"/>';
			// .( $f & self::F_BOLD ? '<b/>' : '')
			// .( $f & self::F_ITALIC ? '<i/>' : '')
			// .( $f & self::F_UNDERLINE ? '<u/>' : '')
			// .( $f & self::F_STRIKE ? '<strike/>' : '')
			// .( $f & self::F_HYPERLINK ? '<color rgb="FF0563C1"/><u/>' : '')
			$s .= '</font>';
		}
		$s .= '</fonts>';				
		$s .= '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" /></cellStyleXfs>';
		$s .= '<cellXfs count="'.count($this->XF).'">';
		foreach ( $this->XF as $xf ) 
		{
			$align = ($xf[2] === self::A_LEFT ? ' applyAlignment="1"><alignment horizontal="left"/>' : '')
				.($xf[2] === self::A_RIGHT ? ' applyAlignment="1"><alignment horizontal="right"/>' : '')
				.($xf[2] === self::A_CENTER ? ' applyAlignment="1"><alignment horizontal="center"/>' : '');
			$s .= "\n".'<xf numFmtId="'.$xf[0].'" fontId="'.$xf[1].'" fillId="0" borderId="0" xfId="0"'
				.($xf[0] > 0 ? ' applyNumberFormat="1"' : '')
				.($align ? $align . '</xf>' : '/>')
				."\n";
		}
		$s .= '</cellXfs>';
		$s .= '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';
		file_put_contents (($tmp."/xl/styles.xml"), $s);


		$fd = fopen ($tmp."/xl/sharedStrings.xml", "w");
		if (!count($this->SI)) $this->SI[] = 'No Data';
		$si_cnt = count ($this->SI);
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="'.$si_cnt.'" uniqueCount="'.$si_cnt.'">';
		fwrite ($fd, $s);
		for ($i=0; $i<$si_cnt; $i++)
		{
			$s = '<si><t>'.$this->SI[$i] ."</t></si>\r\n";
			fwrite ($fd, $s);
		}
		$s = '</sst>';
		fwrite ($fd, $s);
		fclose ($fd);
				
		$fd = fopen ($tmp."/xl/worksheets/sheet1.xml", "w");
		$col_cnt = count ($this->COL);
		$ref = 'A1:'.$this->num2name ($col_cnt) . $this->CUR_ROW;
		$s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><dimension ref="'.$ref.'"/><cols>';
		foreach ( $this->COL as $k => $max )
		{
			$s .= '<col min="'.$k.'" max="'.$k.'" width="'.min( $max+1, 60).'" />';
		}
		$s .= '</cols><sheetData>';
		fwrite ($fd, $s);
		fseek ($fd_sheet,0);
		stream_copy_to_stream ($fd_sheet, $fd); // {ROWS}
		$s = '</sheetData>';
		//{HYPERLINKS}
		$s .= '</worksheet>';
		fwrite ($fd, $s);
		fclose ($fd);	
		fclose ($fd_sheet); 
		
		$zip = new ZipArchive ();
		$xlsxf = $u."_".$doc_ts.".xlsx";
		$rt = $zip->open (("/tmp/".$xlsxf), ZipArchive::CREATE);
		error_log ("zip open ".$rt);
		foreach ($files as $file) 
		{
			$rt = $zip->addFile ($tmp."/".$file, $file);
			error_log ("zip addFile ".$rt);
		}
		$zip->close ();
		
		unlink ($tmp.'/_sheet1_');
		foreach ($files as $file) unlink ($tmp."/".$file);
		$n = count($dirs);		
		for ($i=$n-1; $i>-1; $i--) rmdir ($tmp."/".$dirs[$i]);
		rmdir ($tmp);
		
		return $xlsxf;
	}
}

function _xlsx_download ($u, $res, $join)
{
	$x = new XLSXGen();
	$filename = $x->xlsx_gen ($u, $res, $join);
	$filesize = filesize ($filename);
	header('Content-type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
	header('Content-Disposition: attachment; filename="'.$filename.'"');
	header('Last-Modified: ' . date('D, d M Y H:i:s' , time() ));
	header('Content-Length: '.$filesize);
	header('Cache-Control: no-cache');
        header("Content-Transfer-Encoding: binary");
       	readfile (("/tmp/".$filename));
       	exit (0);
}

?>
