
const XLSX_T_STRING = 0;
const XLSX_T_UINT16 = 1;
const XLSX_T_UINT32 = 2;
const XLSX_T_SINT16 = 3;
const XLSX_T_SINT32 = 4;
const XLSX_T_SU8 = 10;

var CRC_TABLE = [];

function SU8 () 
{
	this.i = 0,
	this.j = 0,
	this.n = 0,
	this.b = [],
	
	this.rst = function () { this.i=0; this.j=0; this.n=0; this.b=[new Uint8Array (1024)]; return this; },
	
	this.set = function (v)
	{
		for (var i=0; i<v.length; i++)
		{
			if (this.j>1023)
			{
				this.i++;
				this.j=0;
				this.b[this.i] = new Uint8Array (1024);
			}
			this.b[this.i].set ([v[i]], this.j);
			this.j++;
			this.n++;
		}
		// console.log (v.length+", "+this.j)
	},
	
	this.append = function (s, t=0)
	{
		if (t==XLSX_T_SU8) // SU8 object
		{
			var i_=0, j_=0;
			for (var i=0; i<s.n; i++)
			{
				if (j_>1023) { i_++; j_=0; }
				var ch = s.b[i_][j_];
				this.set ([ch]);
				j_++;
			}
			// console.log (" xlsx_t_sub "+s.n+" | "+i_+","+j_);
			return;
		}
		
		if (t==XLSX_T_SINT16) // 1 = v unsigned short (always 16 bit, little endian byte order)
		{
			var s16 = new Int16Array ([(s*1)]);
			var s8 = new Int8Array (s16.buffer); 
			for (var i=0; i<2; i++) { this.set ([s8[i]]); }
		}
		
		if (t==XLSX_T_UINT32) // 2 = V unsigned long (always 32 bit, little endian byte order)
		{
			var u32 = new Uint32Array ([(s*1)]);
			var u8 = new Uint8Array (u32.buffer); // return litte endian byte order bits
			for (var i=0; i<4; i++) this.set ([u8[i]])
			return;
		}
		
		if (t==XLSX_T_UINT16) // 1 = v unsigned short (always 16 bit, little endian byte order)
		{
			var u16 = new Uint16Array ([(s*1)]);
			var u8 = new Uint8Array (u16.buffer); // return litte endian byte order bits
			for (var i=0; i<2; i++) { this.set ([u8[i]]); }
		
			//var s16 = new Int16Array ([(s*1)]);
			//var s8 = new Int8Array (s16.buffer); // return litte endian byte order bits
			// console.log ("XLSX_T_UINT16: "+s+" |"+u8+" | "+u16)
			
			return;
		}
		
		for (var i=0; i<s.length; i++) // default = unicode (utf16) string => convert utf16 to utf8
		{
			var ch = s.charCodeAt (i);
			// console.log ("u-----------------"+ch)
			if (ch < 0x80) 
			{
				// console.log ("ascii");
				this.set ([ch]);
				continue;
			}
        		if (ch < 0x800) 
        		{
        			// console.log ("0x800");
				this.set ([0xc0 | (ch >> 6), 0x80 | (ch & 0x3f)]);
				continue;
        		}
        		if (ch < 0xd800 || ch >= 0xe000) 
        		{
        		      	// console.log ("0xd800");
				this.set ([0xe0 | (ch >> 12),  0x80 | ((ch>>6) & 0x3f),  0x80 | (ch & 0x3f)]);
				continue;
        		}
			// console.log ("surrogate");
        		// else // surrogate pair
			// UTF-16 encodes 0x10000-0x10FFFF by
        		// subtracting 0x10000 and splitting the
        		// 20 bits of 0x0-0xFFFFF into two halves
        		i++;
        		if (i>=s.length) break;
        		var ch_ = s.charCodeAt (i);
			ch = 0x10000 + (((ch & 0x3ff)<<10) | (ch_ & 0x3ff));
			this.set ([0xf0 | (ch >>18), 0x80 |  ((ch>>12) & 0x3f),  0x80 | ((ch>>6) & 0x3f),  0x80 | (ch & 0x3f)]);
		}
	}
}	

var XLSX = 
{
	
	N_NORMAL : 0, // General
	N_INT : 1, // 0
	N_DEC : 2, // 0.00
	N_PERCENT_INT : 9, // 0%
	N_PRECENT_DEC : 10, // 0.00%
	N_DATE : 14, // mm-dd-yy
	N_TIME : 20, // h:mm
	N_DATETIME : 22, // m/d/yy h:mm
	
	A_DEFAULT : 0,
	A_LEFT : 1,
	A_RIGHT : 2,
	A_CENTER : 4,
	A_TOP : 8,
	A_MIDDLE : 16,
	A_BOTTOM : 32,
	
	F_NORMAL : 0,
	F_HYPERLINK : 1,
	F_BOLD : 2,
	F_ITALIC : 4,
	F_UNDERLINE : 8,
	F_STRIKE : 16,
	
	CUR_ROW : 0,
	XF : [ [this.N_NORMAL, this.A_DEFAULT, this.F_NORMAL] ],
	XF_KEYS : { 'N0A0F0':0 }, // cellXfs
	SI : [],
	SI_KEYS : {}, // shared strings

	defaultFont : "Calibri",
	defaultFontSize : "10.5",
	
	cdrec : new SU8 (),
	fb : new SU8 (),
	fz : new SU8 (),
};

XLSX.esc = function (v) 
{
	// XML UTF-8: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
	// but we use fast version
	v = v.replace ('&','&amp;')
	v = v.replace ('<', '&lt;'); 
	v = v.replace ('>', '&gt;'); 
	v = v.replace ("\x00", '');
	v = v.replace ("\x03", '');
	v = v.replace ("\x0B", '');
	return v;
}

XLSX.date2excel = function (yr, mn, dy, h=0, m=0, s=0) 
{
	var vt = ((h * 3600) + (m * 60) + s) / 86400;

	if (y === 0) return v
        
	// self::CALENDAR_WINDOWS_1900
	var excel1900isLeapYear = true;
	var excelBaseDate = 2415020;
	if ((parseInt (y) === 1900) && (m <= 2)) { excel1900isLeapYear = false; }
	//    Julian base date Adjustment
	if (m > 2) m -= 3;
	else { m += 9; y--; }
	//    Calculate the Julian Date, then subtract the Excel base date (JD 2415020 = 31-Dec-1899 Giving Excel Date of 0)
	var century = substr (y,0,2);
	var decade = substr (y,2,2);
	var v =   Math.floor ((146097 * century) / 4) 
		+ Math.floor ((1461 * decade) / 4) 
		+ Math.floor ((153 * m + 2) / 5) 
		+ parseInt (d) 
		+ 1721119 - excelBaseDate + excel1900isLeapYear;
	return  (v*1.0) + (vt*1.0);
}
	
XLSX.cell_name = function (i, j) 
{
	var num = (j - 1) % 26;
	var letter  = String.fromCharCode (65 + (num*1));
	var num2    = parseInt ((num-1) / 26);
	if (num2>0) return XLSX.cell_name (num2) + letter + i;
	return (""+letter+i);
}

XLSX.xlsx_val_str = function (v, ct) // ct [ N=0, A=0, F=0, FL=0, C=0, B=0, INLINE:0|SHAREDSTRING:1 ]
{
	var v_ = v;
	var vl = v.length;
	var m = v.match (/^[-+]?[1-9]\d{0,14}$/g);
	if (v==="0" || m!=null)  // Integer as General
	{
		if (v.substr (0,1)=="+") v_ = v.substr (1);
		if (vl > 10) ct[0] = XLSX.N_INT;
		return v_;
	} 
	m = v.match (/^[-+]?(0|[1-9]\d*)\.(\d+)$/);
	if (m!=null)
	{
		if (v.substr (0,1)=="+") v_ = v.substr (1);
		if (m[2].length<3) ct[0] = XLSX.N_DEC;
		return v_;
	}
	m = v.match (/^([-+]?\d+)%$/);
	if (m!=null)
	{
		v_ = Math.round (m[1] / 100, 2);
		ct[0] = XLSX.N_PERCENT_INT; // [9] 0%
		return v_;
	} 
	m = v.match (/^([-+]?\d+\.\d+)%$/);
	if (m!=null)
	{
		v_ = Math.round (m[1] / 100, 4 );
		ct[0] = XLSX.N_PRECENT_DEC; // [10] 0.00%
		return v_;	
	}
	m = v.match (/^(\d\d\d\d)-(\d\d)-(\d\d)$/);
	if (m!=null)
	{
		v_ = XLSX.date2excel (m[1], m[2], m[3]);
		ct[0] = XLSX.N_DATE; // [14] mm-dd-yy
		return v_;
	} 
	m = v.match (/^(\d\d)\/(\d\d)\/(\d\d\d\d)$/);
	if (m!=null)
	{
		v_ = XLSX.date2excel (m[3], m[2], m[1]);
		ct[0] = XLSX.N_DATE; // [14] mm-dd-yy
		return v_;
	}
	m = v.match (/^(\d\d):(\d\d):(\d\d)$/);
	if (m!=null)
	{
		v_ = XLSX.date2excel (0, 0, 0, m[1], m[2], m[3]);
		ct[0] = XLSX.N_TIME; // time
		return v_;
	} 
	m = v.match (/^(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)$/);
	if (m!=null)
	{
		v_ = XLSX.date2excel (m[1], m[2], m[3], m[4], m[5], m[6]);
		ct[0] = XLSX.N_DATETIME; // [22] m/d/yy h:mm
		return v_;
	}
	m = v.match (/^(\d\d)\/(\d\d)\/(\d\d\d\d) (\d\d):(\d\d):(\d\d)$/);
	if (m!=null)
	{
		v_ = XLSX.date2excel (m[3], m[2], m[1], m[4], m[5], m[6]);
		ct[0] = XLSX.N_DATETIME; // [22] m/d/yy h:mm
		return v_;
	}
	m = v.match (/^[0-9+-.]+$/); // Long ?
	if (m!=null)
	{			
		ct[1] = XLSX.A_RIGHT;
		return v_;
	}
	
	v_ = XLSX.esc (v); // removed tags that cn messup xlsx xml

	if (v_ > 160) 
	{
		ct[6] = 1; // 'inlineStr';
		return v_;
	} 
	
	ct[6] = 2; // 's' shared string
	var skey = '~' + v_;
	var vi_ = XLSX.SI_KEYS [skey]
	if (vi_===undefined) 
	{
		vi_ = XLSX.SI.length;
		XLSX.SI_KEYS[skey] = vi_;
		XLSX.SI[vi_] = v_;
	}
	return vi_;
}

XLSX.xlsx_val = function (v, ct)
{
	
	if (typeof v === 'string' || v instanceof String)
	{
		return XLSX.xlsx_val_str (v, ct);
	} 
	if (Number.isFinite (v)===true) 
	{
		//var m = v%1;
		// vl = (""+v).length;
		return v;
	}
	return null;
} 

XLSX.xlsx_cell = function (i, j, v)
{
	var CT = ["","inlineStr","s"]
	var ct = [0,0,0,0,0,0,0]; // [ N=0, A=0, F=0, FL=0, C=0, B=0, INLINE:0|SHAREDSTRING:1, len ]
	var v_ = XLSX.xlsx_val (v, ct); 
	var cs = 0;
	if (ct[0] + ct[1] + ct[2] > 0 ) 
	{
		var NAF = 'N' + c[0] + 'A' + c[1] + 'F' + c[2];
		cs = XLSX.XF_KEYS[NAF];
		if (cs === undefined) 
		{
			cs = XLSX.XF.length;
			XLSX.XF_KEYS[NAF] = cs;
			XLSX.XF[cs] = [c[0], c[1], c[2]];
		}
	}
	var cname = XLSX.cell_name (i,j);
	var s = '<c r="' + cname + '"'
	if (ct[6]>0) s += ' t="'+CT[ct[6]]+'"';
	if (cs>0) s += ' s="'+cs+'"';
	s += '>';
	if (v_===null) v_ = "";
	if (ct[6] === 1) s += '<is><t>'+v_+'</t></is>';
	if (ct[6] !=1) s += '<v>'+v_+'</v>';
	s += "</c>\r\n";
	XLSX.fb.append (s);
}

XLSX.xlsx_row_end = function ()
{
	var s = "</row>\r\n";
	XLSX.fb.append (s);
}

XLSX.xlsx_row_start = function (i)
{
	var s = "<row r=\""+i+"\">";
	XLSX.fb.append (s);
}

XLSX.xlsx_sheet_end = function ()
{
	var s = '</sheetData>';
	s += '<drawing r:id="rId1"/>';
	//{HYPERLINKS}
	s += '</worksheet>';
	XLSX.fb.append (s);
}

XLSX.xlsx_sheet_start = function (title)
{
	var s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" \
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">';
	s += '<sheetFormatPr customHeight="1" defaultColWidth="14.43" defaultRowHeight="15.0"/>';
	s += '<sheetData>';
	s += '<row r="1" ht="33.75" customHeight="1"/>'; // todo: title
	s += '<row r="2" ht="173.25" customHeight="1"/>'; // chart space
	XLSX.fb.rst().append (s);
}

XLSX.xlsx_crc32 = function () 
{
	var i_=0, j_=0;
	var crc = 0 ^ (-1);
	for (var i=0; i<XLSX.fb.n; i++ ) 
	{
		if (j_>1023) { i_++; j_=0; }
		var ch = XLSX.fb.b[i_][j_];
		crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ ch) & 0xFF];
		j_++;
	}
	return (crc ^ (-1)) >>> 0;
}
	
XLSX.xlsx_file_sub = function (file_name)
{
	var zipSignature = "\x50\x4b\x03\x04"; // local file header signature
	var dirSignature = "\x50\x4b\x01\x02"; // central dir header signature

	// Convert date and time to DOS Format, and set then
	var dt = new Date();
	var seconds = dt.getSeconds();
	if (seconds>=32) seconds = seconds-32
	var r = 
	[
	(dt.getFullYear()-1980).toString(2).padStart(7,"0"), 
	(dt.getMonth()+1).toString(2).padStart(4,"0"), 
	dt.getDate().toString(2).padStart(5,"0"), 
	dt.getHours().toString(2).padStart(5,"0"), 
	dt.getMinutes().toString(2).padStart(6,"0"), 
	seconds.toString(2).padStart(5,"0")
	];
	
	var e = {};
	e['uncsize'] = XLSX.fb.n;
	e['comsize'] = e['uncsize']; // nb: no compression applied
	e['vneeded'] = 10;
	e['cmethod'] = 0;
	e['bitflag'] = 0;
	e['crc_32']  = XLSX.xlsx_crc32 ();
       	e['offset'] = XLSX.fz.n;
	e['external_attributes']  = 32; // (substr($cfilename, -1) === '/'&&!$zdata)?16:32; // Directory or file name
        e['comments']             = '';
	e['moddate'] = 21708; // Number.parseInt (r[0]+r[1]+r[2], 2);	
	e['modtime'] = 26710; // Number.parseInt (r[3]+r[4]+r[5], 2);
	
	// console.log ("DATE: "+e['moddate']+"|"+e['modtime']);

	XLSX.fz.append (zipSignature); 
	XLSX.fz.append (e['vneeded'], XLSX_T_SINT16);	// pack('s', $e['vneeded'])); // version_needed
	XLSX.fz.append (e['bitflag'], XLSX_T_SINT16);	// pack('s', $e['bitflag'])); // general_bit_flag
	XLSX.fz.append (e['cmethod'], XLSX_T_SINT16);	// pack('s', $e['cmethod'])); // compression_method
	XLSX.fz.append (e['modtime'], XLSX_T_SINT16);	// pack('s', $e['modtime'])); // lastmod_time
	XLSX.fz.append (e['moddate'], XLSX_T_SINT16);	// pack('s', $e['moddate'])); // lastmod_date
	// console.log ("------- end dae-time---")
	XLSX.fz.append (e['crc_32'],  XLSX_T_UINT32);	// pack('V', $e['crc_32']));  // crc-32
	XLSX.fz.append (e['comsize'], XLSX_T_UINT32);	// pack('I', $e['comsize'])); // compressed_size
	XLSX.fz.append (e['uncsize'], XLSX_T_UINT32);	// pack('I', $e['uncsize'])); // uncompressed_size
	XLSX.fz.append (file_name.length, XLSX_T_SINT16); // pack('s', mb_strlen($cfilename, '8bit')));   // file_name_length
	XLSX.fz.append (0, XLSX_T_SINT16);		// pack('s', 0));  // extra_field_length
	XLSX.fz.append (file_name);			// $cfilename);    // file_name
	XLSX.fz.append (XLSX.fb, XLSX_T_SU8);		// $this->xlsx_data ($fz, $data, $fb);
	
	// console.log ("fzsub len:"+XLSX.fz.i +","+ XLSX.fz.j +","+ XLSX.fz.n+" | fb:"+XLSX.fb.n+" "+e['offset'])	
		
	XLSX.cdrec.append (dirSignature);
        XLSX.cdrec.append ("\x00\x00");				// version made by
	XLSX.cdrec.append (e['vneeded'], XLSX_T_UINT16);	// ('v', $e['vneeded']); // version needed to extract
	XLSX.cdrec.append ("\x00\x00");				// general bit flag
	XLSX.cdrec.append (e['cmethod'], XLSX_T_UINT16);	// ('v', $e['cmethod']); // compression method
	XLSX.cdrec.append (e['modtime'], XLSX_T_UINT16);	// ('v', $e['modtime']); // lastmod time
	XLSX.cdrec.append (e['moddate'], XLSX_T_UINT16);	// ('v', $e['moddate']); // lastmod date
	XLSX.cdrec.append (e['crc_32'],  XLSX_T_UINT32);	// ('V', $e['crc_32']);  // crc32
	XLSX.cdrec.append (e['comsize'], XLSX_T_UINT32);	// ('V', $e['comsize']); // compressed filesize
	XLSX.cdrec.append (e['uncsize'], XLSX_T_UINT32);	// ('V', $e['uncsize']); // uncompressed filesize
	XLSX.cdrec.append (file_name.length, XLSX_T_UINT16);	// ('v', mb_strlen($cfilename,'8bit')); // file name length
	XLSX.cdrec.append (0, XLSX_T_UINT16);			// ('v', 0);                // extra field length
	XLSX.cdrec.append (e['comments'].length, XLSX_T_UINT16);	// ('v', mb_strlen($e['comments'],'8bit')); // file comment length
	XLSX.cdrec.append (0, XLSX_T_UINT16);			// ('v', 0); // disk number start
	XLSX.cdrec.append (0, XLSX_T_UINT16);			// ('v', 0); // internal file attributes
	XLSX.cdrec.append (e['external_attributes'], XLSX_T_UINT32);	// ('V', $e['external_attributes']); // internal file attributes
	XLSX.cdrec.append (e['offset'], XLSX_T_UINT32);		// ('V', $e['offset']); // relative offset of local header
	XLSX.cdrec.append (file_name);
	XLSX.cdrec.append (e['comments']);	
	
	return 1;
}
    
XLSX.xlsx_file = function (p, is_pie)
{
	var doc_ts = "2022-06-10T10:00:00"; // Date ('Y-m-d\TH:i:s');	        
	var entries = 1; // image already uploaded
	var s = "";
	
	var chart_width = "13030200";
	if (is_pie) chart_width = "1962150";
	
	//s = "Test Content";
	//XLSX.fb.rst().append (s);
	//entries += XLSX.xlsx_file_sub ("[Content_Types].xml");
	
	
	entries += XLSX.xlsx_file_sub ("xl/worksheets/sheet1.xml"); // start with sheet1 -- to enable reuse of this buffer
	
	
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\
\
<Default ContentType="application/xml" Extension="xml"/>\
<Default ContentType="image/png" Extension="png"/>\
<Default ContentType="application/vnd.openxmlformats-package.relationships+xml" Extension="rels"/>\
\
<Override ContentType="application/vnd.openxmlformats-package.core-properties+xml" PartName="/docProps/core.xml"/>\
\
<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml" PartName="/xl/workbook.xml"/>\
\
<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml" PartName="/xl/styles.xml"/>\
<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml" PartName="/xl/sharedStrings.xml"/>\
\
<Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml" PartName="/xl/worksheets/sheet1.xml"/>\
<Override ContentType="application/vnd.openxmlformats-officedocument.drawing+xml" PartName="/xl/drawings/drawing1.xml"/>\
\
</Types>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("[Content_Types].xml");
		
		
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>\
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\
</Relationships>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("_rels/.rels");


	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\
<dcterms:created xsi:type="dcterms:W3CDTF">'+doc_ts+'</dcterms:created></cp:coreProperties>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("docProps/core.xml");
	
	
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>\
</Relationships>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/_rels/workbook.xml.rels");
		

	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\
<fileVersion appName="VoiceApps"/>\
<sheets>\
<sheet name="Sheet1" sheetId="1" state="visible" r:id="rId1"/>\
</sheets>\
</workbook>';	
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/workbook.xml");
		

	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
	s += '<fonts count="'+XLSX.XF.length+'">';
	for (var i=0; i<XLSX.XF.length; i++) 
	{
		s += '<font><name val="'+XLSX.defaultFont+'"/>';
		//if ($this->defaultFontSize) $s .= '<sz val="'.$this->defaultFontSize.'"/>';
		//if ($xf[2] & self::F_BOLD) $s .= '<b/>';
		//if ($xf[2] & self::F_ITALIC) $s .= '<i/>';
		//if ($xf[2] & self::F_UNDERLINE) $s .= '<u/>';
		//if ($xf[2] & self::F_STRIKE) $s .= '<strike/>';
		//if ($xf[2] & self::F_HYPERLINK) $s .= '<u/>';
		//if ($xf[2] & self::F_COLOR) $s .= '<color rgb="'.$xf[4].'"/>';
		s += '</font>';
	}
	s += '</fonts>';				
	s += '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>';
	s += '<borders count="1"><border></border></borders>';
	s += '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" /></cellStyleXfs>';
	s += '<cellXfs count="'+XLSX.XF.length+'">';
	for (var i=0; i<XLSX.XF.length; i++)
	{
		var xf = XLSX.XF[i];
		var align = (xf[1] & XLSX.A_LEFT ? ' horizontal="left"' : '')
                       + (xf[1] & XLSX.A_RIGHT ? ' horizontal="right"' : '')
                       + (xf[1] & XLSX.A_CENTER ? ' horizontal="center"' : '')
                       + (xf[1] & XLSX.A_TOP ? ' vertical="top"' : '')
                       + (xf[1] & XLSX.A_MIDDLE ? ' vertical="center"' : '')
                       + (xf[1] & XLSX.A_BOTTOM ? ' vertical="bottom"' : '');

		s += '<xf numFmtId="'+xf[0]+'" fontId="0" fillId="0" borderId="0" xfId="0"'
                  +  (xf[0] > 0 ? ' applyNumberFormat="1"' : '')
                       // .($F_ID > 0 ? ' applyFont="1"' : '')
                       // .($FL_ID > 0 ? ' applyFill="1"' : '')
		  +  (align.length>0 ? s += ' applyAlignment="1"><alignment'+align+'/></xf>' : '/>');
	}
	s += '</cellXfs>';
	s += '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/styles.xml");


	if (XLSX.SI.length==0) XLSX.SI[0] = 'No Data';
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="'+XLSX.SI.length+'" uniqueCount="'+XLSX.SI.length+'">';
	XLSX.fb.rst().append (s);
	for (var i=0; i<XLSX.SI.length; i++)
	{
		s = '<si><t>'+ XLSX.SI[i] +"</t></si>\r\n";
		XLSX.fb.append (s);
	}
	s += '</sst>';
	XLSX.fb.append (s);
	entries += XLSX.xlsx_file_sub ("xl/sharedStrings.xml");

		
	// --------------
	
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/>\
</Relationships>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/worksheets/_rels/sheet1.xml.rels");
		
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>\
</Relationships>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/drawings/_rels/drawing1.xml.rels");

	// [cx] pie: 1962150		bar: 13030200
	s = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<xdr:wsDr \
xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" \
xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" \
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" \
xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" \
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" \
xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram">\
<xdr:oneCellAnchor>\
<xdr:from> <xdr:col>0</xdr:col> <xdr:colOff>400050</xdr:colOff> <xdr:row>1</xdr:row> <xdr:rowOff>219075</xdr:rowOff> </xdr:from>\
<xdr:ext cx="'+chart_width+'" cy="1743075"/>\
<xdr:pic> \
<xdr:nvPicPr> <xdr:cNvPr id="0" name="image1.png" title="Image"/> <xdr:cNvPicPr preferRelativeResize="0"/> </xdr:nvPicPr>\
<xdr:blipFill> <a:blip cstate="print" r:embed="rId1"/> <a:stretch><a:fillRect/></a:stretch> </xdr:blipFill>\
<xdr:spPr> <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/> </xdr:spPr>\
</xdr:pic>\
<xdr:clientData fLocksWithSheet="0"/>\
</xdr:oneCellAnchor>\
</xdr:wsDr>';
	XLSX.fb.rst().append (s);
	entries += XLSX.xlsx_file_sub ("xl/drawings/drawing1.xml");
		
		
	
		

	// --------------
	
	var dirSignatureE= "\x50\x4b\x05\x06"; // end of central dir signature
	var zipComments = 'Generated by Voiceapps xlsx.js';
	var before_cd = XLSX.fz.n;
		
	// console.log ("BEFORECD: "+before_cd+" | "+XLSX.cdrec.n+" "+entries)
		
	XLSX.fz.append (XLSX.cdrec, XLSX_T_SU8);
	XLSX.fz.append (dirSignatureE);	
	XLSX.fz.append (0, 		XLSX_T_UINT16); // number of this disk
	XLSX.fz.append (0, 		XLSX_T_UINT16); // number of the disk with the start of the central directory
	XLSX.fz.append (entries,	XLSX_T_UINT16); // total # of entries "on this disk"
	XLSX.fz.append (entries, 	XLSX_T_UINT16); // total # of entries overall
	XLSX.fz.append (XLSX.cdrec.n, 	XLSX_T_UINT32);	// size of central dir
	XLSX.fz.append (before_cd, 	XLSX_T_UINT32);	// offset to start of central dir
	XLSX.fz.append (zipComments.length, XLSX_T_UINT16); // .zip file comment length
	XLSX.fz.append (zipComments);

}

