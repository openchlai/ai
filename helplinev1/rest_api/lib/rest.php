<?php

$ERRORS=array();

function _G ($k)
{
	if (isset($_GET[$k])) return $_GET[$k];
	return "";
}

function _P ($k)
{
	if (isset($_POST[$k])) return $_POST[$k];
	return "";
}

function _S ($k)
{
	if (isset($_SESSION[$k])) return $_SESSION[$k];
	return "";
}

function _V (&$vv,$k)
{
	if (isset($vv[$k])) return $vv[$k];
	return "";
}

function __VESC ($v)
{
	// error_log ("VESC:".$v);
	//$a = array ("\r","\n","\t",'\r','\n','\t');
	//$v = str_replace ($a, " ", $v); 
	//$v = str_replace ("\\", "", $v); 
	//$v = str_replace ("\"", "'", $v); 
	$v_ = $v; 
	// $v_ = preg_replace ('/[[:^print:]]/', ' ', $v_);  // todo: put flag for removing non:print xters // default:allow
	$n  = strlen ($v_);
	if ($n>0)
	{
		$v_ = json_encode (("".$v_));
		$n = strlen ($v_);
		if ($n>2) $v_ = substr ($v_,1,$n-2); // remove quotes
	}
	$v_ = str_replace ("<", "&lt;", $v_); 
	$v_ = str_replace (">", "&gt;", $v_); 
	return $v_;
}

function _date ($fmt, $v)
{
	if ($v==0) return "";
	return date ($fmt, $v);
}

function _enum ($fmt, $v)
{
	$nn = explode (':',$fmt);		
	if ( !isset ($GLOBALS[($nn[2]."_enum")])) return $v;
	$vv = explode (",", $v);
        $vn = count ($vv);
        $enum_ = $GLOBALS[($nn[2]."_enum")];
        $v="";
        $vc=0;
	for ($iv=0; $iv<$vn; $iv++)
	{
		$v_ = "".$vv[$iv];
		if (strlen ($v_)<1) continue;
		if (isset ($enum_[$v_])) 
		{
			if (!isset ($enum_[$v_][$nn[4]])) error_log ("enum_error: ".$nn[2]." | ".$v_);
			$v_=$enum_[$v_][$nn[4]];
		}
		if ($vc>0) $v.=',';
		$v .= $v_;
		$vc++;
        }
        return $v;
}

function model_k_id ($u, $suffix, &$a)
{
        $t = $GLOBALS["RESOURCES"][$u][0];
        $ta = $GLOBALS["RESOURCES"][$u][1];
        if (strlen($ta)<1) $ta=$t;
        $k = $ta.$suffix."_".$a[0][0];
        if (strlen ($a[0][1])>0) $k = $a[0][1].$suffix;
        return $k;
}

function _kv ($k, &$op, &$o, &$p)
{
	$v = NULL;
	$op = '=';
	if (substr ($k,0,1)==':') 
	{ 
		$vv = explode (":",$k); 
		$op=$vv[1]; 
		$k=$vv[2];  
		if (!isset ($o[$k]) && isset ($vv[3])) 
		{
			$k = $vv[3]; // set default and case_activity_add
			if ($vv[3]==" null") return ("null"._val_id ()."-"._rands (9,"num"));
		}
		if ($op=="")
		{
			// error_log ("---".json_encode ($o));
			$k = $vv[3]; // set default and case_activity_add
			if (isset ($o[$vv[2]]) && strlen ($o[$vv[2]])>0) $k = $vv[4];
		        if (isset ($p[$vv[2]]) && strlen ($p[$vv[2]])>0) $k = $vv[4];	
		}
		if ($op=="@#") return (_val_id ()."-"._rands (9,"num"));
	}
	if (isset ($o[$k])) $v = __VESC ($o[$k]);
	if (isset ($p[$k])) $v = $p[$k];
	if (substr ($k,0,1)==' ') $v = substr ($k,1);
	return $v;
}

function _phone_fmt ($s)
{
	$a = 0;
	$n = strlen ($s);
	for ($i=0; $i<$n; $i++) 
	{
		$ch = substr ($s,$i,1);
		if ($ch=="+" || $ch=="0" || $ch==" ") { $a++; continue; }
		break;
	}
	// error_log ("phone_fmt: ".$a." ".$n." '".substr ($s,$a,($n-$a))."'" );
	if ($n-$a==9) return $GLOBALS["COUNTRY_CODE"].substr ($s,$a,($n-$a));
	return substr ($s, $a, ($n-$a));
}

function _rands ($n,$k)
{
        $ch = array
	(
		'num'=>'0123456789',
		'alpha'=>'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
		'ascii'=>'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@!#$abcdefghijklmnopqrstuvwxyz',
	);
	$chn = array ('num'=>9, 'alpha'=>61, 'ascii'=>65);
	$s = '';
        for ($i=0; $i<$n; $i++) {
        	$s .= $ch[$k][ rand (0, $chn[$k])];
        }
	return $s;
}

function _str2ts ($str)
{
	$_s_ = [ 
	"all"=>["0",""], 
	"today"=>["1","d F Y"], 
	"this_week"=>["2","F Y"], 
	"this_month"=>["3","1 F Y"], 
	"this_year"=>["4","Y"], 
	"last_3_month"=>["5","90"], "last_6_month"=>["5","180"], "last_9_month"=>["5","270"] ];
	
	$t1 = time ();
	if (!isset ($_s_[$str])) return "";
	$k = $_s_[$str];
	if ($k[0]=="0") return "";
	if ($k[0]=="1") 
	{
		$t0 = strtotime (date($k[1], $t1)); 
		return $t0;
	}
	if ($k[0]=="2") // find 
	{
		$d = date ("w");
		$t0 = strtotime (date("d F Y", $t1)); 
		$t0 -= ($d*3600*24);
		return $t0.";".$t1;
	}
	if ($k[0]=="3") 
	{
		$t0 = strtotime (date($k[1], $t1)); 
		return $t0.";".$t1;
	}
	if ($k[0]=="4")
	{
		$y = date ("Y",$t1);
		$t0 = strtotime ("1 January ".$y); 
		return $t0.";".$t1;
	}
	if ($k[0]=="5")
	{
		$t1_ = strtotime (date("1 F Y", $t1)); ;
		$t0 = $t1_-($k[1]*3600*24);
		return $t0.";".$t1;
	} 
		return $t0.";".$t1;
}

function qryp ($q, $argt, $argv, $r=0, $db_="db")
{
	$stmt = mysqli_stmt_init ($GLOBALS[$db_]);
	if ($stmt==NULL) 
	{
		error_log ("STMT INIT ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q);
		return NULL;
	}
	if (mysqli_stmt_prepare ($stmt, $q)==FALSE) 
	{
		error_log ("STMT PREPARE ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q);
		return NULL;
	}
	$n = count ($argv);
	if ($n>0)
	{
		$a = array (&$stmt, &$argt);
		for ($i=0; $i<$n; $i++) 
		{
			$argv[$i] = $argv[$i]; 
			$a[] = &$argv[$i]; 
		}
		$ret = call_user_func_array ("mysqli_stmt_bind_param", $a);
		if ($ret!==TRUE) 
		{
			error_log ("STMT BIND ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q." (".$argt."^".$n.") ".json_encode ($argv));
			return NULL;
		}
	}
	$ret = mysqli_stmt_execute ($stmt);
	if ($ret!==TRUE) 
	{ 
		$mysql_error_no = mysqli_errno ($GLOBALS[$db_]);
		error_log ("STMT EXEC ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q." (".$argt."^".$n.") ".json_encode ($argv));
		if ($mysql_error_no==1062) return -3; 
		return NULL; 
	}
	if ($r==1) 
	{
		$res = mysqli_stmt_get_result ($stmt);
		if ($res===FALSE)
		{
			error_log ("STMT RES ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q." (".$argt."^".$n.") ".json_encode ($argv));
			return NULL;
		}
		return mysqli_fetch_array ($res,  MYSQLI_NUM); // 
	}
	if ($r==2)
	{
		//$id = mysqli_stmt_insert_id ($stmt);
		$id = mysqli_insert_id ($GLOBALS[$db_]);
		$mysql_error_no = mysqli_errno ($GLOBALS[$db_]);
		if ($id==0 && $mysql_error_no==0)
		{
			error_log ("STMT INSERT ID:".$id." | ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_]));
			return $argv[0];
		}
		return $id;
	}
	if ($r==3)
	{
		return mysqli_stmt_affected_rows ($stmt);
	}
	if ($r==4) return $ret;
	
	
	$ret = mysqli_stmt_get_result ($stmt);
	if ($ret===FALSE)
	{
		error_log ("STMT RES ERROR: ".mysqli_errno ($GLOBALS[$db_]).":".mysqli_error ($GLOBALS[$db_])." |".$q." (".$argt."^".$n.") ".json_encode ($argv));
		return NULL;
	}
	return $ret;
}


// --------------------------------------------------------------------------------------------

function _select_cols ($u, $prefix, &$q)
{
	$a = $GLOBALS[($u."_def")];
	$n = count ($a);
	for ($j=0; $j<$n; $j++)
	{ 
		if ($j>0) $q.=",";
		$q .= $prefix.$a[$j][0]; 
	}
}

function _select ($u, &$aa, &$av, $db_="db", $join=[]) 
{
	$a = $GLOBALS[($u."_def")];
	$t = $GLOBALS["RESOURCES"][$u][0];		
	$join_n = count ($join);
	$ujoin = null;
	if (isset ($GLOBALS[($u."_join")])) { $ujoin=$GLOBALS[($u."_join")]; }
	$prefix = "";
	$ta = "`".$t."`";
	if (isset ($aa["ta"]) && strlen ($aa["ta"])>0) $ta .= $aa["ta"]; // append join tables
	
	$q = "SELECT ";
	if ($join_n>0) $prefix=$t.".";
	_select_cols ($u, $prefix, $q);
	if (isset ($_GET["xlsx"]) || isset ($_GET["csv"])) // include join column for csv/xlsx downloads
	{
		for ($i=0; $i<$join_n; $i++)
		{
			if (!isset ($ujoin[$join[$i]])) continue;
			$uj = $ujoin[$join[$i]];
			$prefix = $uj[1].".";
			$q .= ",";
			_select_cols ($uj[0], $prefix, $q);
		}
	}
	
	$orderby = " ORDER BY ".$t.".".$a[0][0]." DESC "; // todo eval order by
	if (strlen ($GLOBALS["RESOURCES"][$u][6])>0) $orderby = " ORDER BY ".$GLOBALS["RESOURCES"][$u][6]; 
	if (strlen ($aa["sort"])>0) $orderby = $aa["sort"];
	if (isset ($aa["group"]) && strlen ($aa["group"])>0) $orderby = $aa["group"];

	$q .= " FROM ".$ta." ".$aa["w"]." ".$orderby." ".$aa["lim"];  

	error_log ("       [SELECT] (".$u.") ".$q." |".json_encode ($av));
	
	return qryp ($q, $aa["s"], $av); 
}

function _val_error ($u, $i, $k, $v, $errno, $errmsg)
{
	$GLOBALS["ERRORS"][] = ["error",$errmsg,$errno,$u,$i,$k,$v]; 

	error_log ("    +-- [invalid] ".$k. " ". $errno);

	return 1;
}

function _val_phone (&$v)
{
	$phone_regex = '/^[0-9]{3,15}/';
	if (preg_match ($phone_regex, $v)!=1) return 1;
	$v = _phone_fmt ($v);
	return 0;
}

function _val_email ($v)
{
	if (strlen ($v)<1) return 1;
	$email_regex = '/^(?!(?:(?:\x22?\x5C[\x01-\x7E]\x22?)|(?:\x22?[^\x5C\x22]\x22?)){255,})(?!(?:(?:\x22?\x5C[\x01-\x7E]\x22?)|(?:\x22?[^\x5C\x22]\x22?)){65,}@)(?:(?:[\x21\x23-\x27\x2A\x2B\x2D\x2F-\x39\x3D\x3F\x5E-\x7E]+)|(?:\x22(?:[\x01-\x08\x0B\x0C\x0E-\x1F\x21\x23-\x5B\x5D-\x7F]|(?:\x5C[\x01-\x7F]))*\x22))(?:\.(?:(?:[\x21\x23-\x27\x2A\x2B\x2D\x2F-\x39\x3D\x3F\x5E-\x7E]+)|(?:\x22(?:[\x01-\x08\x0B\x0C\x0E-\x1F\x21\x23-\x5B\x5D-\x7F]|(?:\x5C[\x01-\x7F]))*\x22)))*@(?:(?:(?!.*[^.]{64,})(?:(?:(?:xn--)?[a-z0-9]+(?:-[a-z0-9]+)*\.){1,126}){1,}(?:(?:[a-z][a-z0-9]*)|(?:(?:xn--)[a-z0-9]+))(?:-[a-z0-9]+)*)|(?:\[(?:(?:IPv6:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){7})|(?:(?!(?:.*[a-f0-9][:\]]){7,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?)))|(?:(?:IPv6:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){5}:)|(?:(?!(?:.*[a-f0-9]:){5,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3}:)?)))?(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))(?:\.(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))){3}))\]))$/iD';
	if (preg_match ($email_regex, $v)!=1) return 1;
	return 0;
}

function _val_addr ($o, &$v)
{
	if (!isset ($o["src"])) return 1;
	if (!isset ($GLOBALS["src_enum"][$o["src"]])) return 1;
	if ($GLOBALS["src_enum"][$o["src"]][3]=="1") return _val_phone ($v);		// default address is a phone number
	// todo: address s email
	return 0;
}

function _val_id ()
{
	$ts = gettimeofday (true);
	return floor($ts*10000);
}

function _val ($u, $id, &$o, &$p, &$a, &$v, $istry=0)
{
	$e = 0;

	if ($a[4]=="k") { $v = ($a[5]); return 0; }		// constant
	if ($a[4]=="@") { $v = _val_id (); $v.="."; $v.=_rands (9,"num"); return 0; }		// generate id
	if ($a[4]=="#") { $v = _rands (9,"num"); return 0; }	// generate random number

	$k = $a[0];
	if (strlen($a[1])>0) $k = $a[1];

	$v = NULL;
	if (isset ($o[$k])) $v = __VESC ($o[$k]);
	if (isset ($p[$k])) $v = $p[$k];

	if ($id!=NULL && $v===NULL) return 0; // skip unset during update

	if ($v===NULL && $a[4]=='v') $v=$a[7]; // default value
	
	if (strlen($a[4])==0 && strlen($a[5])==0) return 0;

	if (($a[4]=="m" || $a[4]=="u") && strlen($v)<1) // check mandatory field
		return _val_error ($u, $o["i_"], $k, $v, "REQUIRED", $a[9]." is Required");

	if ($a[4]=="u" && isset ($o[$k]) && isset ($p[$k]))
        {
		$vo = json_decode ("[\"".$p[$k]."\"]");
                if ($vo && strtoupper($o[$k])==strtoupper($vo[0])) // check duplicate field
                        return _val_error ($u, $o["i_"], $k, $v, "DUPLICATE", $a[9]." exists with value of ".$o[$k]);
	}

	if ($a[5]=="e" && strlen ($v)>0 && _val_email ($v)!=0) 
		return _val_error ($u, $o["i_"], $k, $v, "INVALID", "Invalid Email address");

	if ($a[5]=="p" && strlen ($v)>0 && _val_phone ($v)!=0) 
		return _val_error ($u, $o["i_"], $k, $v, "INVALID", ("Invalid Phone Number '".$v."'"));

	if ($a[5]=="P" && strlen ($v)>0 && _val_addr ($o,$v)!=0) 
		return _val_error ($u, $o["i_"], $k, $v, "INVALID", ("Invalid ".$GLOBALS["src_enum"][$o["src"]][2]." '".$v."'"));
		
	if ($a[5]=="r" && strlen ($v)>0 && preg_match ($a[6], $v)!=1) 
		return _val_error ($u, $o["i_"], $k, $v, "INVALID", "Invalid format for ".$a[9]);

	if ($a[3]==1 && $a[5]=="l")
	{
		$min = $a[6];
		$max = $a[7];
		$m = strlen ($v);
		if (strlen ($min)>0 && $m<$min) $e += _val_error ($u, $o["i_"], $k, $v, "INVALID", ($a[9]." length must be at least ".$min));
		if (strlen ($max)>0 && $m>$max) $e += _val_error ($u, $o["i_"], $k, $v, "INVALID", ($a[9]." length Exceed ".$max));
	}

	if ($a[3]==4 && $a[5]=="l")
	{
		$min = $a[6];
		$max = $a[7];
		if (strlen ($min)>0 && $v<$min) $e +=  _val_error ($u, $o["i_"], $k, $v, "INVALID", ($a[9]." Must be at least ".$min)); 
		if (strlen ($max)>0 && $v>$max) $e +=  _val_error ($u, $o["i_"], $k, $v, "INVALID", ($a[9]." Exceeds ".$max)); 
	}

	if ($a[5]=='f' && !isset ($p[$k]) && isset ($o[$k]) && strlen($o[$k])>0 && $o[$k]!="0" && $o[$k]!="-1" && $istry==0)
	{
		return _val_error ($u, $o["i_"], $k, $v, "INVALID_FOREIGN_KEY", $a[9]." does not exist");  
	}
	
	return $e;
}

function _try ($u, $suffix, $id, &$o, &$p)
{
	error_log ("  [try] ".$u);

	$a = $GLOBALS[($u."_def")];
	$n = count ($a);
	$c=0;
	$e=0;	
	for ($i=1; $i<$n; $i++)
	{ 
		$v = null;
		$e += _val ($u, $id, $o, $p, $a[$i], $v, 1); 
	} 
	if ($e>0) return -2;
	return $id;
}

function _upd ($u, $suffix, $id, &$o, &$p, $fm=2)
{
	if (strlen ($id)<1) return 0;

	$a = $GLOBALS[($u."_def")];
	$t = $GLOBALS["RESOURCES"][$u][0];		
	$k = model_k_id ($u, $suffix, $a);
	
	$_dup = array ($u,"","dup",$a[0][0],$k,NULL,"*"); // generate audit trail record -- retrieve existing record
	$o_ = [];
	$p_ = [];
	if (isset ($o[$k])) $o_ = [$k=>$o[$k]];
	if (isset ($p[$k])) $p_ = [$k=>$p[$k]];
	_dup ($_dup, $o_, $p_);
	
	$aub_id = 0;
	if (isset ($p["aub_id"])) $aub_id = $p["aub_id"];

	$q = "UPDATE `".$t."` SET "; //updated_on=UNIX_TIMESTAMP(Now()), updated_by=\"".__S("cc_user_usn")."\", updated_by_id=\"".__S("cc_user_id")."\"";
	$argt = "";
	$argv = [];
	$n = count ($a);
	$c=0;
	$e=0;	
	for ($i=1; $i<$n; $i++)
	{ 
		if ($a[$i][2]!=$fm && $a[$i][2]!=3) continue;

		$v = null;
		$e += _val ($u, $id, $o, $p, $a[$i], $v); 
		if ($v===null) continue;
		
		if (isset ($p_[$a[$i][0]]) && $v==$p_[$a[$i][0]])  continue;
	
		$q_ = "INSERT INTO au(aub_id,t,row_id,k,v,v_) VALUES(?,?,?,?,?,?)"; // log change in column // 
		$argt_ = "ssssss";
		$v_="";
		if (isset ($p_[$a[$i][0]])) $v_=$p_[$a[$i][0]];
		$argv_ = [$aub_id,$u,$id,$a[$i][0],$v,$v_];
		$id_ = qryp ($q_, $argt_, $argv_, 2); 
		if ($id_==NULL) error_log (" [au](".$u.") ERROR audit trail save failed! ".$k."|".$id);

		if ($c>0) $q .= ",";
		$q .= $a[$i][0]."=?"; 
		$argt .= "s";
		$argv[$c] = $v;
		$c++;
	} 
	
	if ($c<1) return $id; // 0
	
	$q .= " WHERE ".$a[0][0]."=?";
	$argt .= "s";
	$argv[$c] = $id;

	//if ($rights!=NULL) // todo: row level update access  -- similar to read access
	//{
	//	
	//}

	if ($e>0 && $GLOBALS["RESOURCES"][$u][4]==0) return -2;

	error_log ("       [UPD] (".$u.$suffix.") ".$q." |".json_encode ($argv));
	$res = qryp ($q, $argt, $argv, 4); 
	if ($res==NULL) return -2;
	return $id;
}

function _add ($u, $suffix, &$o, &$p) 
{
	$t = $GLOBALS["RESOURCES"][$u][0];
	$q = "INSERT INTO `".$t."`(";
	$qv = ", created_on, created_by, created_by_id, created_by_role) VALUES(";
	$argt = "";
	$argv = [];
	
	$a = $GLOBALS[($u."_def")];
	$t = $GLOBALS["RESOURCES"][$u][0];
	$subset = null;
	if (isset ($GLOBALS[($u.$suffix.'_subset')])) $subset = $GLOBALS[($u.$suffix.'_subset')];
	$n = count ($a);
	$c=0;	
	$e=0;

	for ($i=0; $i<$n; $i++)
	{ 
		if ($a[$i][2]!=1 && $a[$i][2]!=3) continue;
		if ($subset!=NULL && !isset ($subset [$a[$i][0]])) continue;
		$v = null;
		$e += _val ($u, NULL, $o, $p, $a[$i], $v); 
		if ($c>0) { $q.=","; $qv.=","; }
		$q .= $a[$i][0]; 
		$qv .= "?";
		$argt .= "s";
		if ($v===null) $v="";
		$argv[$c] = $v;
		$c++;
	}
	
	if ($c<1) return 0;

	$q .= $qv.", UNIX_TIMESTAMP(Now()),?,?,?)";
	$argt .= "sss";
	$argv[$c] = _S("cc_user_usn");
	$argv[($c+1)] = _S("cc_user_id"); 
	$argv[($c+2)] = _S("cc_user_role"); 

	if ($e>0 && $GLOBALS["RESOURCES"][$u][4]==0) return -2;

	error_log ("       [ADD] (".$u.$suffix.") ".$q." |".json_encode ($argv));
	$id =  qryp ($q, $argt, $argv, 2); 
	if ($id==-3)
	{
		_val_error ($u, $o["i_"], "", "", "DUPLICATE", ("Unique Key Violation ".$u));
		return -3;
	}
	return $id;
}

// ------------------------------------------------------------------------------------------------------ 

function _csv_cols_v ($u, $row, $start)
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
		if ($a[$j_][3]==3 && strlen ($v)>0) { $v = _date ($a[$j_][10], $v); }
		if ($a[$j_][3]==2 && strlen($a[$j_][10])>0) { $v = _enum ($a[$j_][10], $v); }
		if ($j>0) echo ",";
		echo '"'.$v.'"';
	}
	return count ($a);
}

function _csv_cols_k ($u)
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
        	if ($j>0) echo ",";
                echo '"'.strtoupper($a[$j_][9]).'"';
	}        
}

function _csv_download ($u, &$aa, $join)
{

        header("Content-Type: text/csv");
        //header("Content-Length: " . filesize($s));
        //header('Content-Description: File Download');
        header('Content-Disposition: attachment; filename="'.$u.'.csv"');
        //header('Expires: 0');
        //header('Cache-Control: must-revalidate');
        //header('Pragma: public');
        header("Content-Transfer-Encoding: binary");

	$nj = 0;
	$uj = null;
	if (isset ($GLOBALS[($u."_join")])) { $nj=count ($join);  $uj=$GLOBALS[($u."_join")]; }
			
	_csv_cols_k ($u);
	for ($i=0; $i<$nj; $i++)
	{
		if (!isset ($uj[$join[$i]])) continue;
		echo ',';
		_csv_cols_k ($uj[$join[$i]][0]);
	}
        echo "\r\n";

        while (($row = mysqli_fetch_row ($aa['res'])))
        {
        	$start = _csv_cols_v ($u, $row, 0);
		for ($i=0; $i<$nj; $i++)
		{
			if (!isset ($uj[$join[$i]])) continue;
			echo ',';
			$start += _csv_cols_v ($uj[$join[$i]][0], $row, $start);
		}
                echo  "\r\n";
        }
	exit (0);
}

function _file_download ($u, &$aa, $f)
{
	$row = mysqli_fetch_row ($aa['res']);
	if ($row==NULL) return 404;

	$uid = $row[0];
        $mime = "application/octet-stream"; // todo pick from RESOURCE
        $kk = $GLOBALS[($u."_k")];
        $ff = array ();
        if (isset ($GLOBALS[($u."_folders")])) $ff = $GLOBALS[($u."_folders")];
        $s = DAT."/".$u."/";
        if (isset ($ff[$f])) { $s.=$ff[$f][0]."/"; $mime=$ff[$f][1]; }
        $s .= $row[0];
        if ($u=="vfiles") $s.=".wav";
	if ($u=="calls") 
	{
		$s .= ".ogg";
		$mime = 'audio/ogg'; // 'audio/ogg';
		$found = file_exists ($s);
		if (!$found)
		{
			$q = "sox ".DAT."/calls/".$uid.".gsm ".DAT."/calls/".$uid.".ogg 2>&1";
			$aa = shell_exec ($q);
			error_log ("[shell exec] ". $q." | ". $aa);
		}
		$found = file_exists ($s);
		if (!$found)
		{
			copy_from_pabx ($uid);
		}
	}

	$found = file_exists ($s);
	
	error_log ("FILE DOWNLOAD: ".$s." | ". ($found===true?'true':'false')); 

	if ($found!==true) return 404;

        if (isset ($kk["mime"])) $mime = $row[$kk["mime"]]; 

	// todo: update read status function

        // send the right headers
        header("Content-Type: " . $mime);
        header("Content-Length: " . filesize($s));
        //header('Content-Description: File Download');
	if (isset ($kk["name"])) header('Content-Disposition: attachment; filename="'.$row[$kk["name"]].'"');
        //header('Expires: 0');
        header('Cache-Control: no-cache');
        //header('Pragma: public');
        header("Content-Transfer-Encoding: binary");
	$n = readfile ($s);
	error_log ("FILE DOWNLOAD: ".$s." | ".$found ."|".$n);
	//sleep (2);
       return 0;
}

function ur (&$row, &$a, $n, $fmt, $i, $l)
{
	$fmt_start = array ('[','[','{','','[');
	$fmt_end = array (']',']','}','',']');
	if ($fmt==1) echo '"'.$row[0].'":';
	echo $fmt_start[$fmt];
	for ($j=0; $j<$n; $j++) 
	{
		if ($j>0) echo ",";
		if ($fmt==2 || $fmt==3)
		{
			$k = $a[$j][0];
			if (strlen ($a[$j][1])>0) $k = $a[$j][1];
			echo '"'.$k.'":';
		}
		$v = $row[$j]; // nb: already escaped during saving
		echo '"'.$v.'"';
	} 
	if ($fmt==0) echo ',"'.$i.'","ro'.$i.'","rc'.$l.'"'; // append metadata if fmt==0
	echo $fmt_end[$fmt];
	echo "\n";
}

function rpt_col ($u, &$a, &$kk, $v)
{
	$SORTDESC = ["yr"=>1, "mn"=>1, "wk"=>1, "dt"=>1, "dth"=>1, "h"=>1];
	$sort = "";
	if (isset ($SORTDESC[$v])) $sort = " DESC ";
	$vv = explode ("^",$v);
	$vn = count ($vv);
	if ($vn==1)
	{
		if (!array_key_exists ($vv[0], $kk)) return NULL;
		$j = $kk[$v];
		if ($a[$j][3]!="2" && $a[$j][3]!="3") return NULL;
		return [$v, $GLOBALS['RESOURCES'][$u][0], $a[$j][0], $a[$j][3], $a[$j][10], $sort, ("".$j)];
	}
	if (!isset ($GLOBALS[($vv[0]."_k")])) return NULL;
	$kk_ = $GLOBALS[($vv[0]."_k")];
	$a_ = $GLOBALS[($vv[0]."_def")];
	if (!array_key_exists ($vv[1], $kk_)) return NULL;
	$j = $kk_[$vv[1]];
	if ($a_[$j][3]!="2" && $a_[$j][3]!="3") return NULL;
	return [$v, $GLOBALS['RESOURCES'][$vv[0]][0], $a_[$j][0], $a_[$j][3], $a_[$j][10], $sort, ("".$j)];
}

function rpt_cols ($u, &$a, &$kk, &$v, $n, &$gg)
{
	for ($i=0; $i<$n; $i++) 
	{ 
		$gg[$v[$i]] = rpt_col ($u, $a, $kk, $v[$i]);
	}
}


function rpt ($u, $suffix, &$fo, &$aa, &$av, $join) 
{	
	$mm = $GLOBALS["METRICS"];
	
	$a = $GLOBALS[($u."_def")];
	$t = $GLOBALS["RESOURCES"][$u][0];
	$kk = $GLOBALS[($u."_k")];
	$n = count ($a);
	$ta = $t;
	if (isset ($aa["ta"])) $ta .= $aa["ta"];

	$xx = explode (",", _V($fo,"xaxis"));
	$yy = explode (",", _V($fo,"yaxis"));
	$zz = explode (",", _V($fo,"metrics"));
	$xn = 0; 
	$yn = 0; 
	$zn = 0; 
	if (strlen (_V($fo,"xaxis"))>0) $xn = count ($xx);
	if (strlen (_V($fo,"yaxis"))>0) $yn = count ($yy);
	if (strlen (_V($fo,"metrics"))>0) $zn = count ($zz);
	
	$xx_ = [];
	$yy_ = [];
	$zz_ = [];
	$xm = 0;
	$ym = 0;
	$zm = 0;
	$sm = 0;
	$sm_ = 0;
	
	$c = 0;
	$i = 0;
	$m = null;
	$s = "";
	
	$gg = [];
	rpt_cols ($u,$a,$kk,$xx,$xn,$gg);
	rpt_cols ($u,$a,$kk,$yy,$yn,$gg);
	$gl = count($gg)-1;
	error_log ("[rpt_cols] ".json_encode ($gg));
	
	for ($i=0; $i<$xn; $i++) 
	{ 
		$ak = $gg[$xx[$i]];
		if ($ak==NULL) continue;
		$xx_[$xm] = $ak;
		$xm++;
		if ($i==$xn-1)
		{
			error_log ("[rpt_metric] ".$zz[0]." | ".$ak[1]."_count");
			$zz[0] = $ak[1]."_count"; // auto switch count_metric to the last column			
		}
	}

	for ($i=0; $i<$yn; $i++) 
	{ 
		$ak = $gg[$yy[$i]];
		if ($ak==NULL) continue;
		$yy_[$ym] = $ak;
		$ym++;
	}

	$x="";
	$y="";
	$z="";
	$g="";
	$gx="";
	$gy="";
	$gz="";
	$gs="";
	$sfmt = '';

	$s .= '"'.$u.$suffix.'_z":{';   
	for ($i=0; $i<$zn; $i++)
        {
                if (!isset ($mm[$zz[$i]])) continue;
                $m = $mm[$zz[$i]];
		if ($zm>0) { $z.=','; $gz.=','; $s.=','; }
		$z .= $zz[$i];
		$gz .= $m[0];
                $s .= '"'.$zz[$i].'":"'.$zm.'"';
                $zz_[$zm] = $m;
                $zm++;
                if (strlen ($m[1])>0) $sm++; // count subqueries
		if (strlen ($m[4])>0) $sm_++; // count subquery columns
                if (strlen ($m[6])>0)
                {
                        $s_ = " WHERE ";
                        if (strlen ($aa["w"])>0) $s_ = " && ";
                        $aa["w"] .= $s_.$m[6];  // todo: parameters
                }
        }
	if ($zm<1) // default metric: count
	{ 
		$m = $mm["count"];
		$s .= '"count":"0"';
		$zz_[$zm] = $m;
		$zm++; 
	}
	$s .= '},';

	if (($xm+$ym+$sm_)<1) 
	{
		$q = "SELECT COUNT(*) FROM ".$ta.$aa["w"]; // TODO: use correct metric(s) instead of COUNT(*)
		$aa['res'] = qryp ($q, $aa["s"], $av); 
		if ($aa['res']==NULL) return 404;
		
		$aa["rptjn"] = 1;
		$aa['rpt']  = $s;
		return 200;
	}

	$s .=  '"'.$u.$suffix.'_x":[';
	for ($j=0; $j<$xm; $j++) 
	{ 
		if ($j>0) { $x.=','; $g.=','; $gx.=','; $gs.=','; $s.=','; $sfmt.=','; }
		$x .= $xx_[$j][0]; 
		$g .= $xx_[$j][1].'.'.$xx_[$j][2]; 
		$gx .= $xx_[$j][1].'.'.$xx_[$j][2]; 		
		$gs .= $xx_[$j][1].'.'.$xx_[$j][2].$xx_[$j][5];
		$s .= '"'.$xx_[$j][0].'"';
		$sfmt .= '"'.$xx_[$j][4].'"';
	}
	for ($j=0; $j<$zm; $j++) // subquery columns
	{ 
		if (strlen ($zz_[$j][4])<1) continue;
		if ($xm>0 || $j>0) { $x.=','; $g.=','; $gx.=','; $gs.=','; $s.=','; $sfmt.=','; }
		$x .= $zz_[$j][4]; 
		$g .= $zz_[$j][4];
		$gx .= $zz_[$j][4];
		$gs .= $zz_[$j][4];
		$s .= '"'.$zz_[$j][4].'"';
		$sfmt .= '"'.$zz_[$j][5].'"';
	}
	$s .=  '],';

	$s .= '"'.$u.$suffix.'_y":[';
	for ($j=0; $j<$ym; $j++) 
	{
		if ($xm>0 || $sm_>0 || $j>0) { $g.=','; $gs.=','; $sfmt.=','; }
		if ($j>0) { $y.=','; $s.=','; }
		$y .= $yy_[$j][0];
		$g .= $yy_[$j][1].'.'.$yy_[$j][2]; 		
		$gs .= $yy_[$j][1].'.'.$yy_[$j][2].$yy_[$j][5];
		$sfmt .= '"'.$yy_[$j][4].'"';
		$q = "SELECT ".$yy_[$j][1].".".$yy_[$j][2]." FROM ".$ta.$aa["w"]." GROUP BY ".$yy_[$j][1].".".$yy_[$j][2].$yy_[$j][5];
		error_log ("--> [RPT-y] (".$u.") ".$q." | ".json_encode ($av));
		$res = 	qryp ($q, $aa["s"], $av); 
		if ($j>0) $s .= ',';  
		$s .= '[';
		if ($res!=NULL)
		{
			$n = 0;
			while ($row = mysqli_fetch_row ($res))
			{
				if ($n>0) $s .= ',';
				$s .= '"'.$row[0].'"';
				$n++;
			}
		}
		$s .= ']';
	}
	$s .= '],';

	$s .= '"'.$u.$suffix.'_fmt":['.$sfmt.'],';

	$s .= '"'.$u.$suffix.'_rpt":[["'.$u.'","'.$x.'","'.$y.'","'.$z.'"]],'; 

	$s .= '"rpt":[["'.$u.'","'.$x.'","'.$y.'","'.$z.'"]], '; 

	$qz = "SELECT ".$g.",".$gz." FROM ".$ta.$aa["w"]." GROUP BY ".$gs; 

	for ($j=0; $j<$zm; $j++) // generate totals for subquerys
	{ 
		if (strlen ($zz_[$j][1])<1) continue;

		$m = $zz_[$j];
		$g_ = $m[1];  		// NB m[1] col is omited in outer query
		$gs_ = $m[1];
		if (($xm+$sm_)>0) { $g_.=",".$gx; $gs_.=",".$gx; }
		$q = "SELECT ".$gx.",".$m[3]." FROM (SELECT ".$g_.",".$m[2]." FROM ".$ta.$aa["w"]." GROUP BY ".$gs_.") tb0 GROUP BY ".$gx;
		error_log ("--> [RPT-xtot] (".$u.") ".$q." | ".json_encode ($av));
		$res = null;
		if (strlen ($gx)>0) $res = qryp ($q, $aa["s"], $av); 
		$s .= '"'.$u.$suffix.'_xtot":{';
		if ($res!=NULL)
		{
			$n = 0;
			while ($row = mysqli_fetch_row ($res))
			{
				if ($n>0) $s .= ',';
				$s .= '"'.$row[0].'":"'.$row[1].'"'; // todo: more than one xaxis columns
				$n++;
			}
		}
		$s .= '},';

		// todo: _ytot

		$q = "SELECT ".$m[3]." FROM ".$ta.$aa["w"];
		error_log ("--> [RPT-gtot] (".$u.") ".$q." | ".json_encode ($av));
		$row = 	qryp ($q, $aa["s"], $av, 1); 
		if ($row!=NULL)
		{
			$s.='"'.$u.$suffix.'_gtot":"'.$row[0].'",';
		}

		$g_ = $m[1].','.$g;
		$gs_ = $m[1].','.$gs;
		$qz = "SELECT ".$g.",".$gz." FROM (SELECT ".$g_.",".$m[2]." FROM ".$ta.$aa["w"]." GROUP BY ".$gs_.") tb0 GROUP BY ".$gs;
	}

	error_log ("--> [RPT] (".$u.$suffix.") ".$qz." | ".json_encode ($av));
	$aa['res'] = 	qryp ($qz, $aa["s"], $av); 
	if ($aa['res']==NULL) return 404;
	
	$aa["rpt_jn"] = $xm+$sm_+$ym+$zm;
	$aa["rpt"]  = $s;
	return 200;
}

function k_ft ($t, $k, $v, &$aa, &$av)
{
	error_log ("k_ft: ".$k."=".json_encode ($v)); // MATCH(fullname) AGAINST('+jinja' IN BOOLEAN MODE)
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	$c = 0;
	for ($j=0; $j<$n; $j++) if (strlen($v[$j])>0)
	{ 
		if ($c==0) $aa["w"] .= $s."(";
		if ($c>0) $aa["w"] .= " && ";
		$aa["w"] .= $t.'.'.$k." REGEXP ?"; 
		$aa["s"] .= "s";
		$av[] = '[ \\^]'.$v[$j]."|^".$v[$j];
		$c++;
	}
	if ($c>0) $aa["w"] .= ")"; 
	
	$aa["sort"] = " ORDER BY ".$k;
}

function k_n ($t, $k, $v, &$aa, &$av)
{
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	if ($n==1 && strlen(trim($v[0]))>0) { $aa["w"] .= $s.$t.'.'.$k."=?"; $aa["s"].="s"; $av[]=$v[0]; }
	if ($n==2 && strlen(trim($v[0]))>0 && strlen(trim($v[1]))>0) { $aa["w"] .= $s.$t.'.'.$k.">=? && ".$t.'.'.$k."<=?"; $aa["s"].="ss"; $av[]=$v[0]; $av[]=$v[1]; } 
}

function k_d ($t, $k, $v, &$aa, &$av)
{
	error_log ("k_d: ".json_encode ($v));

	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	if ($n>0)  
	{ 
		$aa["w"] .= $s."(".$t.'.'.$k.">=?"; 
		$aa["s"].="s"; 
		$v_ = $v[0];
		//$dt = DateTime::createFromFormat ('Y-m-d H:i:s', (trim($v[0])." 00:00:00")); 
		//if ($dt!=null) $v_ = $dt->getTimestamp ();
		$av[] = $v_; 
	} 
	if ($n==1) 
	{ 
		$aa["w"] .= " && ".$t.'.'.$k."<?)"; 
		$aa["s"].="s"; 
		$v_ = "".($v[0]+86400);
		//$dt = DateTime::createFromFormat ('Y-m-d H:i:s', (trim($v[0])." 23:59:59"));
		//if ($dt!=null) $v_ = $dt->getTimestamp ();
		$av[] = $v_; 
	} 
	if ($n>1)  
	{ 
		$aa["w"] .= " && ".$t.'.'.$k."<?)";  
		$aa["s"].="s";  
		$v_ = "".($v[1]+86400);
		//$dt = DateTime::createFromFormat ('Y-m-d H:i:s', (trim($v[1])." 23:59:59")); 
		//if ($dt!=null) $v_ = $dt->getTimestamp ();
		$av[] = $v_; 
	} 
}

function k_ch ($t, &$a, $v, &$aa, &$av) // hierachical enum -- match level
{
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	$c = 0;
	$cw = [];
	$ci = [];
	for ($j=0; $j<$n; $j++) if (strlen($v[$j])>0) 
	{
		$q = "SELECT ".$a[12]." FROM ".$a[11]." WHERE id=?";
		$av_ = [$v[$j]]; 
		$row = qryp ($q, "s", $av_, 1);
		if ($row==NULL) continue;
		$k = $row[0]-1;
		if (!isset ($ci[$k])) { $ci[$k]=$c; $cw[$c]=$t.'.'.$a[13].$k." IN (?"; $c++; }
		else $cw[$ci[$k]] .= ",?"; 
		$aa["s"] .= "s";
		$av[] = $v[$j];
	}
	if ($c>0) $aa["w"] .= $s."("; 
	for ($j=0; $j<$c; $j++)
	{
		if ($j>0) $aa["w"] .= ' || ';
		$aa["w"] .= $cw[$j].")";
	}
	if ($c>0) $aa["w"] .= ")";
	error_log ( " >> hie ".$aa["w"]);
}

function k_c ($t, $k, $v, &$aa, &$av)
{
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	$c = 0;
	for ($j=0; $j<$n; $j++) if (strlen($v[$j])>0) 
	{
		if ($c==0) $aa["w"] .= $s.$t.'.'.$k." IN (";
		if ($c>0) $aa["w"] .=","; 
		$aa["w"] .= "?"; //mysqli_real_escape_string($GLOBALS["db"],$v[$j])."\""; 
		$aa["s"] .= "s";
		$av[] = $v[$j];
		$c++;
	}
	if ($c>0) $aa["w"] .= ")";
}

function k_s ($t, $k, $v, &$aa, &$av)
{
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	$c = 0;
	for ($j=0; $j<$n; $j++) if (strlen($v[$j])>0)
	{ 
		if ($c==0) $aa["w"] .= $s."(";
		if ($c>0) $aa["w"] .= " || ";
		$aa["w"] .= $t.'.'.$k." LIKE ?"; //.mysqli_real_escape_string ($GLOBALS["db"],$v[$j])."%\" ";
		$aa["s"] .= "s";
		$av[] = "%".$v[$j]."%";
		$c++;
	}
	if ($c>0) $aa["w"] .= ")";
}

function ctx_fv ($t, $m, $v, &$a, &$aa, &$av)
{
	if ($m==1) k_s ($t, $a[0], explode (",",$v), $aa, $av);
	if ($m==2) k_c 	($t, $a[0], explode (",",$v), $aa, $av);
	if ($m==3) k_d 	($t, $a[0], explode (";",$v), $aa, $av);
	if ($m==4) k_n 	($t, $a[0], explode ("-",$v), $aa, $av);
	if ($m==6) k_c 	($t, $a[0], explode (",",$v), $aa, $av);
	if ($m==9) k_ft ($t, $a[0], explode (" ",$v), $aa, $av); // fulltext search
	if ($m==12)k_ch ($t, $a,    explode (",",$v), $aa, $av); // hie-enum
}

function ctx_f ($u, &$aa, &$av, &$fo, $is_join=0) // parse GET parameters
{
	$a = $GLOBALS[($u."_def")];
	$t = $GLOBALS["RESOURCES"][$u][0];
	$n = count ($a);
	$c = 0;
	for ($i=0; $i<$n; $i++)
	{
		$m = $a[$i][3];
		$k = $a[$i][0];
		if (strlen($a[$i][1])>0) $k=$a[$i][1];
		if ($is_join==1) { $k = $u."^".$k; }

		if (isset ($fo[($k.'__i')]) && strlen ($fo[($k.'__i')])>0) // eval index.php filters
		{ 
			ctx_fv ($t, $m, $fo[($k.'__i')], $a[$i], $aa, $av);
		} 		
		
		$v = NULL;
		if (isset ($fo[$k])) $v = $fo[$k];
		if (isset ($fo[($k.'__')])) { $v=$fo[($k.'__')]; $m=9; } // using dash double-dash coz there are fields ending with
		if ($v===NULL && $is_join==1) continue; 		 // skip blanks for join (only add columns filtered with)	
		if ($v!==NULL && strlen ($v)>0)
		{
			if (isset ($a[$i][11])) $m=12;
			ctx_fv ($t, $m, $v, $a[$i], $aa, $av);
		}
		if ($v==NULL) $v="";
		if ($c>0) { $aa["f"] .= ','; }
		$aa["f"] .= '"'.$k.'":["'.$i.'","'.$k.'","'.__VESC($v).'","'.$a[$i][9].'","'.$a[$i][10].'"]';
		$c++;
	}
}

function ctx ($u, $suffix, &$aa, &$av, &$fo, &$join)
{
	$a = $GLOBALS[($u."_def")];
	$kk = $GLOBALS[($u."_k")];
	$t = $GLOBALS["RESOURCES"][$u][0];
	
	$_a = 0;
	$_c = 20;
	$c = 20;
	$title = "";
	$sort = "";
	$gl = "";
	
	if (isset ($fo["_a"])) $_a = ($fo["_a"]*1);
	if (isset ($fo["_c"])) { $_c = ($fo["_c"]*1); $c=$_c; }
	if (isset ($fo["__c"])) $_c = ($fo["__c"]*1); // c override
	if ($_c>1) $_a -= ($_a % $_c); // align _a
	if (isset ($fo["_o"])) $_a = $_a+($fo["_o"]*1);
	if (isset ($fo["_title"])) $title = $fo["_title"];

	$jc = [""," LEFT JOIN "," INNER JOIN "," INNER JOIN "];
	$jo = [];
	if (isset ($fo["join"])) // generate join clause
	{ 
		$jj = explode (",",$fo["join"]); 
		$jn = count ($jj);
		for ($j=0; $j<$jn; $j++) if (strlen  ($jj[$j])>0) $jo[$jj[$j]]="1";
	} 
	
	$gk = [];
	if (isset ($fo["xaxis"])) { $gk = explode (",",($fo["xaxis"].",".$fo["yaxis"])); error_log ("-->".json_encode ($gk)); }
	$gkn = count ($gk);
	for ($i=0; $i<$gkn; $i++) // generate join from rpt xaxis,yaxis columns
	{
		if (strlen ($gk[$i])<1) continue; // skip blank params
		$vv = explode ("^",$gk[$i]);
		if (count($vv)<2) continue;
		if (strlen  ($vv[0])>0) $jo[$vv[0]] = "3";
	}
	
	$wk = array_keys ($fo); 
	$wkn = count ($wk);
	for ($i=0; $i<$wkn; $i++) // generate join from filter colums
	{
		if (strlen ($fo[$wk[$i]])<1) continue; // skip blank params
		$vv = explode ("^",$wk[$i]);
		if (count($vv)<2) continue;
		if (strlen  ($vv[0])>0) $jo[$vv[0]] = "2"; 
	}

	// error_log ("   ctx joins ---->".json_encode ($jo));
	
	$join = array_keys ($jo);
	$join_n = count ($join);
	$ujoin = null;
	if (isset ($GLOBALS[($u."_join")])) { $ujoin=$GLOBALS[($u."_join")]; }
	
	
	$aa["ta"] = "";
	$aa["f"] .= '"'.$u.$suffix.'_k":{';
	ctx_f ($u, $aa, $av, $fo);
	for ($i=0; $i<$join_n; $i++)  // join clause
	{
		if (!isset ($ujoin[$join[$i]])) continue;
		$uj = $ujoin[$join[$i]];
		$aa["ta"] .= $jc[$jo[$join[$i]]]."`".$uj[1]."` ON ".$uj[2];
		if ($jo[$join[$i]]==3) continue; // skip rpt columns
		$aa["f"] .= ","; 
		ctx_f ($uj[0], $aa, $av, $fo, 1);
	}
	//if (isset ($fo["group"])) $aa["f"] .= ',"group":"'.$fo["group"].'"';
	$aa["f"] .= '}';
	
	if (isset ($fo["sort"])) 
	{	
		$vv = explode (",",$fo["sort"]);
		$n = count ($vv);
		$d = "";
		for ($j=0; $j<$n; $j++)
		{
			if (!isset ($kk[$vv[$j]])) continue;
			$sort .= $d.$a[$kk[$vv[$j]]][0];
			if ($kk[$vv[$j]]==0) $sort .= " DESC";
			$d=',';
		}
		if (strlen ($sort)>0) $aa["sort"] = " ORDER BY ".$sort;
	}
		
	if (isset ($fo["group"])) 
	{	
		$group = "";
		$vv = explode (",",$fo["group"]);
		$n = count ($vv);
		$d = "";
		for ($j=0; $j<$n; $j++)
		{
			if (!isset ($kk[$vv[$j]])) continue;
			$group .= $d.$a[$kk[$vv[$j]]][0];
			$d=',';
			$gl = $a[$kk[$vv[$j]]][0];
		}
		if (strlen ($group)>0) $aa["group"] = " GROUP BY ".$group;
	}
	
	$cf = 'COUNT('.$t.'.'.$a[0][0].')';
	if ($join_n>0) $cf = 'COUNT(DISTINCT '.$t.'.'.$a[0][0].')'; // todo : count based on last join table
	if (isset ($aa["group"])) $cf = 'COUNT(DISTINCT '.$t.'.'.$gl.')';
	$q = 'SELECT '.$cf.' FROM `'.$t.'`'.$aa['ta'].' '.$aa['w'];  
	error_log ("   [CTX] (".$u.") ".$q);
	
	$row = qryp ($q, $aa["s"], $av, 1); 
	$_n = $row[0];
	$_m = $_n%$_c;
	if ($_m==0 && $_n>0) $_m=$_c;
	$_l = $_n-$_m;
	if ($_a<0) $_a=0;
	if ($_a>$_l) $_a=$_l;

	$a_ = $_a;
	if ($_n>0) $a_++;
	$c_ = $_a+$_c;
	if ($c_>$_n) $c_=$_n;
	
	$aa["lim"] = " LIMIT ".$_a.",".$_c;

	$aa["ctx"] = '"'.$u.$suffix.'_ctx":[["'.$_a.'","'.$c.'","'.$a_.'","'.$c_.'","'.$_n.'","'.$title.'","'.$sort.'"]]';
}

function ctx_rights ($u, &$aa, &$av, &$p, &$rights)
{
	$t = $GLOBALS["RESOURCES"][$u][0];
	$s = " WHERE ";
	if (strlen ($aa["w"])>0) $s = " && ";
	$n = count ($rights);
	$c = 0;
	for ($i=5; $i<$n; $i+=2)
	{
		$k = $rights[($i+1)];
		if (strlen ($k)>0 && !isset ($p[$k])) { error_log ("ctx-right fail ".$k); return -1; }
		$aa["w"].=$s;
		if ($c==0) $aa["w"].="(";
		$aa["w"] .= $t.'.'.$rights[$i];
		if (strlen ($k)>0)
		{
			$aa["w"] .= "?";
			$aa["s"] .= "s";
			$av[] = $p[$k];
		}
		$s = " || ";
		$c++;
	}
	if ($c>0) $aa["w"].=") ";
	return 0;
}

// ------------------------------------------------------------------------------------------------------

function csv_upload ($u, $t, $i, &$p)
{
	$file_tmp_name = $_FILES[$t]["tmp_name"][$i];
	$file_name = $_FILES[$t]["name"][$i];
	$vv = explode (".", $file_name);
	$n = count ($vv);

	if ($n<2 || $vv[$n-1]!="csv")
	{
		return _val_error ($u, $i, "File Format", "", "INVALID", "Upload Failed. File should be CSV Format!"); 
	}

	$fd = fopen ($file_tmp_name, "r");
	if (!$fd)
	{
		return _val_error ($u, $i, "System Error", "", "INVALID", "Upload Failed!"); 
	}

	$p['csv_data_nb'] = '"csv_data_nb":[["error","No records found"]]';
	$p['csv_data_k'] = '"csv_data_k":{"0":["","","?","",""], "1":["","","?","",""], "2":["","","?","",""], "3":["","","?","",""] }';
	$p['csv_data'] = '"csv_data":[';

	$r = -1;
	while (($data = fgetcsv ($fd, 4000, ",")) !== FALSE) 
	{
		$r++;

		$jn = count ($data);

		if ($r==0)
		{
			$p['csv_data_k'] = '"csv_data_k":{';
			for ($j=0; $j<3; $j++)
			{
				$v = '?';
				if ($jn>$j) $v = $data[$j];
				if ($j>0) $p['csv_data_k'] .= ',';
				$p['csv_data_k'] .= '"'.$j.'":["","","'.$v.'","",""]';
			}
			$p['csv_data_k'] .= '}';
			continue;
		}

		if ($r>10) continue;

		if ($r>1) $p['csv_data'] .= ',';
		$p['csv_data'] .= '[';		
		for ($j=0; $j<3; $j++)
		{
			$v = '?';
			if ($jn>$j) $v = __VESC ($data[$j]);
			if ($j>0) $p['csv_data'] .= ',';
			$p['csv_data'] .= '"'.$v.'"';
		}
		$p['csv_data'] .= ']';
	}

  	fclose ($fd);

	if ($r>0) $p['csv_data_nb'] = '"csv_data_nb":[["info","'.$r.' records found"]]';

	$p['csv_data'] .= ']';

	return 0;
}

function _file_upload ($u, $suffix, &$o, &$p)
{
	$i = $o["i_"];
	$t = $GLOBALS["RESOURCES"][$u][0];
	
	$o["id"] = _val_id ();
	$o["name"] = $_FILES[$t]["name"][$i];
	$o["mime"] = $_FILES[$t]["type"][$i];
	$o["size"] = $_FILES[$t]["size"][$i];
	$o["uploadstatus"] = $_FILES[$t]["error"][$i];
	$o["movestatus"] = "fail";
	$s = $o["id"];
	$f = $_FILES[$t]["tmp_name"][$i];

	error_log ("  file_upload: id=".$o["id"]." | ".$i." | ".json_encode ($_FILES[$t]["error"][$i]));
	if ($_FILES[$t]["error"][$i]!=0)
	{
		_val_error ($u, $i, "File Size", $out[0], "INVALID", "Upload Failed. file size exceeds allowed size!"); 
		return -2;
	}
	
	if ($u=="csv")
	{
		$e = csv_upload ($u, $t, $i, $p);
		if ($e>0) return -2;
	}

	if ($u=="vfiles") // todo validate: voicefile and get duration
	{
		$s.=".wav";
		$out=null;
		$ret=[null,null,null,null];
		exec (('soxi -t '.$f), $out, $ret[0]);
		error_log ( "  [soxi] -t ".$f." | ".$ret[0]." |".json_encode ($out));
		if ($ret[0]!=0)
		{
			_val_error ($u, $i, "File Format", $out[0], "INVALID", "Upload Failed. Not a wav file!"); 
			return -2;
		}
		exec (('soxi -r '.$f), $out, $ret[1]);
		exec (('soxi -c '.$f), $out, $ret[2]);
		exec (('soxi -D '.$f), $out, $ret[3]);
		error_log ( "  [soxi] ".json_encode ($ret) ." | ".json_encode ($out));
		$e = 0;
		if ($ret[1]!=0 || $out[1]!="8000") { $e++;   _val_error ($u, $i, "Sample Rate", $out[1], "INVALID", "Sample rate should be 8000Hz");    }
		if ($ret[2]!=0 || $out[2]!="1") { $e++;   _val_error ($u, $i, "Channels", $out[2], "INVALID", "Channels should be single/mono channel");   }
		if ($e>0) return -2;

		$o["channels"] = $out[1];
		$o["sample_rate"] = $out[2];
		$o["duration"] = $out[3];

	}

	error_log ("   move file: ".(DAT."/".$u."/".$s));
	
	if ($o["uploadstatus"]==0 && move_uploaded_file ($_FILES[$t]["tmp_name"][$i], (DAT."/".$u."/".$s))) // 
	{
		$o["movestatus"] = "ok";
	}
	else 
	{
		// todo: log error
		_val_error ($u, $i, "Destination", "id", "INVALID", "Upload Failed. Permission denied!"); 
		return -2;
	}

	$id = _add ($u, $suffix, $o, $p);
	
	// if () return -2;
	
	return $o["id"];
}

function _lvl (&$b, &$o, &$p) // array ("contacts","","lvl","location_fullname_id","7","^",":", "location","id",""), // gen levels
{
	error_log ("[lvl] ".$b[0]);
	$k = $b[3];
	if (!isset ($p[$k])) 
	{
		error_log ("    --> lvl:".$b[0]." ".$k." is not set"); 
		return; 
	}
	$vv = explode ($b[5], $p[$k]);
	$n = count ($vv);
	for ($i=0; $i<$b[4]; $i++) 
	{
		$vv_ = ["0",""];
		if ($i<$n && strlen ($vv[$i])>0) $vv_ = explode ($b[6], $vv[$i]);
		$p[($b[7].$b[8].$i)] = $vv_[0];
		$p[($b[7].$b[9].$i)] = $vv_[1];
		error_log ("    --> lvl:".$b[7].$i."=".$vv_[0].",".$vv_[1]."|".$n);
	}
}

function _params (&$b, &$o, &$p)
{
	$bn = count ($b);
	error_log ("[params] ".$b[0]." | ".$bn);
	for ($i=3; $i<$bn; $i+=2)
	{
		$op = '=';
		$k = $b[($i+1)];
		$v = _kv ($k, $op, $o, $p);
		if ($v===null) continue;
		if ($op!="+") $p[$b[$i]] = "";
		$p[$b[$i]] .= $v;
		error_log ("    --> param: ".$i.": ".$b[$i]."=".$p[$b[$i]]."|".$k);
	}
}

function _dup (&$b, &$o, &$p)
{
	error_log ("[dup] ".$b[0]);

	$aa = array ("ctx"=>"", "f"=>"", "w"=>" WHERE ", "s"=>"", "sort"=>"", "lim"=>"");
	$av = [];
	$bn = count ($b);
		
	$a = $GLOBALS[($b[0]."_def")];
	$kk = $GLOBALS[($b[0]."_k")];
	$t = $GLOBALS["RESOURCES"][$b[0]][0];
	$ta = $GLOBALS["RESOURCES"][$b[0]][1];
	if (strlen ($ta)<1) $ta=$t;

	$e=0;
	$i=3;
	while ($b[$i]!=NULL)
	{
		if ($i>3) $aa["w"] .= '&& ';
		$op = '=';
		$k = $b[($i+1)];
		$v = _kv ($k, $op, $o, $p);
		if ($v===null) { $e++; error_log ("    --x dup '".$k."' isnull"); } 
		$aa["w"] .= $b[$i].$op."? "; 
		$aa["s"] .= "s";
		$av[] = $v;
		$i += 2;
	}

	$i++;
	$row = NULL;

	if ($e==0)
	{
		$res = _select ($b[0], $aa, $av);
		if ($res!=NULL) $row = mysqli_fetch_row ($res);
	}

	if ($row==NULL)
	{
		if ($b[2]=="duf" && $e==0) // clear field-txt value eg location_id, location
		{
			for ($i; $i<$bn; $i++) 
			{
				$vv = explode (":",$b[$i]);
				$vn = count ($vv);
				$j = $kk[$vv[0]];
				$k = $ta."_".$vv[0];
				if (strlen ($a[$j][1])>0) $k = $a[$j][1];
				if ($vn>1) $k = $vv[1];	
				$p[$k] = "";
				error_log ("    --> udup: ".$i.") ".$k);
			}
		}
		return NULL;
	}
	
	if ($b[$i]=="*") // used mainly by upd
	{
		$n = count ($a);
		for ($i=1; $i<$n; $i++) $p[$a[$i][0]] = $row[$i];
		error_log ("    --> dup: *");
		return $row;
	}
	
	for ($i; $i<$bn; $i++)
	{
		$vv = explode (":",$b[$i]);
		$vn = count ($vv);
		$j = $kk[$vv[0]];
		$k = $ta."_".$vv[0];
		if (strlen ($a[$j][1])>0) $k = $a[$j][1];
		if ($vn>1) $k = $vv[1];
		$v = $row[$j];	
		
		if ($vn>2 && $vv[2]=="s") // skip field if exists in api request ($o)
		{
			error_log ("*****skip******".$k."|".( array_key_exists ($k, $o)?"TRUE":"FALSE"));
			if (array_key_exists ($k, $o)) continue;
		}
			
		$p[$k] = "".$v;
		error_log ("    --> dup: ".$i."(".$j.") ".$k."=".$v);		
	}
	
	return $row;	
}

function _agg (&$b, &$o, &$p)
{
	error_log ("[".$b[2]."] ".$b[1]."->".$b[0]." ");
	//error_log ("    --> [p]: ".json_encode ($p));
	
	$u = $b[0];
	$t = $GLOBALS["RESOURCES"][$u][0];
	$u_ = $b[1];
	$t_ = $GLOBALS["RESOURCES"][$u_][0];
	$a = $GLOBALS[($u."_def")];
	$an = count ($a);	
	$m = substr ($b[2],3,1);	
	$bn = count ($b);	
	$c = 0;
	$e = 0;	
	$q = "UPDATE ".$t." SET ";
	$q_ = "SELECT ";
	for ($i=0; $i<$an; $i++)	// SELECT / UPDATE columns
	{
		if ($a[$i][2]!=$m) continue;
		if ($a[$i][6]!=$u_) continue;
		if ($c>0) { $q.=","; $q_.=","; }
		$q .= $a[$i][0]."=?";
		$q_ .= $a[$i][7];
		$c++;
	}
	$q .= ' WHERE ';
	$q_ .= ' FROM '.$t_.' WHERE ';

	if ($c<1) { error_log ("    --x agg error:  c:".$c); return; }

	$av__ = [];
	$c = 0;
	$i = 3;
	while ($b[$i]!=NULL)		// UPDATE WHERE CLAUSE
	{
		$op = '=';
		$k = $b[($i+1)];
		$v = _kv ($k, $op, $o, $p);
		if ($v===NULL) { error_log ("    --x agg error uclause: ".$k." isnull"); $e++; break; }
		if ($c>0) $q .= '&& ';
		$q .= $b[$i].$op.'? '; 
		$av__[] = $v;
		$c++;
		$i+=2;
	}

	if ($e>0) { error_log ("    --x agg error uclause  e:".$e); return; }

	$av_ = [];
	$ds_ = "";
	$c = 0;
	$i++;
	while ($i<$bn)		// SELECT WHERE CLAUSE
	{
		$op = '=';
		$k = $b[($i+1)];
		$v = _kv ($k, $op, $o, $p);
		if ($v===NULL) { error_log ("    --x agg error sclause: ".$k." isnull"); $e++; break; }
		if ($c>0) $q_ .= '&& ';
		$q_ .= $b[$i].$op.'? '; 
		$av_[] = $v;
		$ds_ .= "s";
		$c++;
		$i+=2;
	}
	
	if ($e>0) { error_log ("    --x agg error sclause  e:".$e); return; }
	
	error_log ("    -- agg ".$q_."|".$ds_."|".json_encode ($av_));
	
	$row = qryp ($q_, $ds_, $av_, 1);
	
	if ($row==NULL) { error_log ("    --x agg error sclause nodata"); return; }
	
	$av = [];
	$ds = "";
	$c = 0;
	for ($i=0; $i<$an; $i++)
	{
		if ($a[$i][2]!=$m) continue;
		if ($a[$i][6]!=$u_) continue;
		$ds .= 's';
		$av[] = "".$row[$c];
		if (strlen($a[$i][8])>0) { $p[$a[$i][8]] = $row[$c]; } 
		$c++;
	}
	$n = count ($av__);
	for ($i=0; $i<$n; $i++) 
	{  
		$av[]=$av__[$i];
		$ds.='s';
	}

	error_log ("    -- agg ".$q."|".$ds."|".json_encode ($av));
	
	qryp ($q, $ds, $av, 3);
}

// ------------------------------------------------------------------------------------------------------ 

function rest_uri_response_error ($rt)
{

	if ($rt == 400)
	{
		header("HTTP/1.0 400 Bad Request");
		header ('Content-Type: application/json');
		echo '{"errors":[["error","Invalid Request"]] }'; 
		return;
	}

	if ($rt == 401)
	{
		header ("HTTP/1.0 401 Authentication Required");
		header ('Content-Type: application/json');
		echo '{"errors":[["error","Authentication Required"]] }'; 
		return;
	}

	if ($rt == 403)
	{
		header("HTTP/1.0 412 Access Denied");
		header ('Content-Type: application/json');
		echo '{"errors":[["error","You do not have rights to update this resource","Access Denied","","",""]]}';
		return;
	}

	if ($rt == 404)
	{
	error_log ("rest_uri_response_error - 404");
		header("HTTP/1.0 404 Not Found");
		header ('Content-Type: application/json');
		echo '{ "errors":[["error","The requested URL '.__VESC($_SERVER["REQUEST_URI"]).' was not found on this server"]]}';
		exit(0);
	}

	if ($rt == 412)
	{
		header("HTTP/1.0 412 Invalid Data");
		header ('Content-Type: application/json');
		$s = json_encode ($GLOBALS["ERRORS"]); // nb: each error-item will have fieldname, tablename, row-index
		echo '{"errors":'.$s.'}';
		return;
	}

	if ($rt == 500)
	{
		header("HTTP/1.0 500 Server Error");
		header ('Content-Type: application/json');
		$s = json_encode ($GLOBALS["ERRORS"]); // nb: each error-item will have fieldname, tablename, row-index
		echo '{"errors":'.$s.'}';
		return;
	}
}

function rest_uri_response ($u, $suffix, $id, &$o, &$p, &$aa, $rt)
{
	// error_log ("[rest_uri_response] ".$u.$suffix."/".$id);

	if ($rt!=0)
	{
		$h = "200 OK";
		if ($rt==201) $h = "201 Created";
		if ($rt==202) $h = "202 Updated";
		header("HTTP/1.1 ".$h);
		header ('Content-Type: application/json');
		echo '{';
	}
	
	$fmt_start = array ('":[', '":{', '":[', '":{', '":[');
	$fmt_end = array (']', '}', ']', '}', ']');
	$fmt = $GLOBALS["RESOURCES"][$u][3];
	$a = $GLOBALS[($u."_def")];
	$an = count ($a);
	$i = 0;
	$l = 0;
	$row = NULL;
	
	if (isset ($aa["rpt"]))
	{
		echo $aa["rpt"]; 
		$an = $aa["rpt_jn"]; 
		$fmt = 4;
	}
	
	echo '"'.$u.$suffix.$fmt_start[$fmt]; 
	if ($id=="-1") 
	{
		echo "[\"-1\"";
		for ($j=1; $j<$an; $j++)  // map any avalable field
		{
			$v="";
			if (isset ($o[$a[$j][0]])) { $v=__VESC($o[$a[$j][0]]); error_log (" --> map: ".$a[$j][0]."=".$v); }
			if (isset ($p[$a[$j][0]])) $v=$p[$a[$j][0]];
			if (strlen ($v)>0 && $a[$j][5]=="p") _val_phone ($v);
			if (strlen ($v)>0 && $a[$j][5]=="P") _val_addr ($o, $v);
			echo ",\"".$v."\"";
		}
		echo "]";
		$i++;
	}
	else
	{
		while ($row = mysqli_fetch_row ($aa['res']))
		{
			if ($i>0) echo ',';
			ur ($row, $a, $an, $fmt, $i, $l); 
			$i++;
			$l++; if ($l>1) $l=0;
			if (isset ($aa['sub_id'])) { $p[$aa['sub_id']] = ("".$row[0]); }
			if ($id!==NULL) break;
		}
	}
	echo $fmt_end[$fmt]."\n";
	 
	if ($i==0) echo ', "'.$u.$suffix.'_no_data":[[]]'."\n";
	
	if (isset($aa["f"])) echo ",".$aa["f"]."\n";
	
	if ($id===NULL) echo ",".$aa["ctx"]."\n";
	
	$bb = [];
	
	//if ($id===NULL && isset ($GLOBALS[($u.$suffix."_rel")]))
	//{
	//	$bb = $GLOBALS[($u.$suffix."_rel")];
	//	$p = $aa['fo'];
	//}

	if ($id!==NULL && isset ($GLOBALS[($u.$suffix."_subs")])) // recursion parameters
	{
		$bb = $GLOBALS[($u.$suffix."_subs")];
		$k = model_k_id ($u, $suffix, $a);
		$p[$k] = $id;
		$n = 0;
		if ($row!=NULL) $n = count ($a);
		for ($j=1; $j<$n; $j++)  // collect fk
		{
			$v=$row[$j];
			if ($a[$j][3]!='2') continue;
			$p[$a[$j][0]] = $v; 
			error_log ("[fk] ".$j." : ".$a[$j][0]." = ".$v);
		}
	}

	// error_log ("[subs-p] ".json_encode ($p));
	// error_log ("[subs-o] ".json_encode ($o));

	$n = count ($bb);
			
	for ($i=0; $i<$n; $i++)
	{
		$aa_ = array ("ctx"=>"", "f"=>"", "w"=>"", "s"=>"", "sort"=>"", "lim"=>"", "res"=>NULL);
		$av_ = [];
		$o_ = $o;
		$p_ = $p;
		$fo_ = [];
		$id_ = NULL;
		$e = 0;
		$b = $bb[$i];
		$fo_["_c"] = 10; 
		if (strlen ($b[2])>0) $fo_["_c"] = $b[2];
		$n_ = count ($b); 
		for ($i_=3; $i_<$n_; $i_+=2)
		{
			$op_ = "=";
			$k_ = $b[($i_+1)];  
			$v_ = _kv ($k_, $op_, $o_, $p_);
			if ($v_===NULL) { error_log ("[sub] (".$b[0].$b[1].")  ".$k_." isnull "); $e++; break; } // then load empty record
			if ($i_==3 && $b[$i_]=="id" && strlen ($v_)<1) $v_="0";
			$fo_[$b[$i_]] = $v_;
			if ($i_==3 && $b[$i_]=="id" && $k_=="case_id") $id_ = $v_; // enable recurion for cases
		}
		if ($e>0) $fo_["id"]="0";
		
		error_log ("[sub] (".$b[0].$b[1].")  id:".$id_." ".json_encode ($fo_)); //  ."|".json_encode ($p)); 
		echo ",";
		$rt_ = rest_uri_get ($b[0], $b[1], $id_, $fo_, $p_, $aa_); // nb: able to return rpt by seting 'metric' params
		if ($rt_==200) rest_uri_response ($b[0], $b[1], $id_, $o_, $p, $aa_, 0);
		// error_log ("[sub-ret<<] (".$b[0].$b[1].")  id:".$id_." | ".$rt_."|".$n); //  ."|".json_encode ($p)); 
	}
	
	if ($rt!=0)
	{
		if ($rt==201) echo ',"'.$u.'_nb":[["info","'.$GLOBALS["RESOURCES"][$u][5].' Created"]]';
		if ($rt==202) echo ',"'.$u.'_nb":[["info","'.$GLOBALS["RESOURCES"][$u][5].' Updated"]]';
		if ($rt==201 && $u=="csv") echo ','.$p['csv_data_k'].','.$p['csv_data_nb'].','.$p['csv_data'];
		echo '}';
	}
	
	return $rt;
}

function rest_uri_get ($u, $suffix, $id, &$fo, &$p, &$aa)
{
	$aa['res'] = NULL;
	$aa["ctx"] = ""; 
	$aa["f"] = ""; 
	$aa["w"] = ""; 
	$aa["s"] = ""; 
	$aa["sort"] = ""; 
	$aa["lim"] = "";
	
	if (!isset ($GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])])) return 404;
	$rights = $GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])];
	if ($rights[$u][0]!="1") return 403; // check read rights flag
	
	$a = $GLOBALS[($u."_def")];
	$k = model_k_id ($u, $suffix, $a);
	$t = $GLOBALS["RESOURCES"][$u][0];
		
	$av = [];
	$join = [];
	
	if ($id===NULL)
	{
		if (ctx_rights ($u, $aa, $av, $p, $rights[$u])!=0) return 403; 
		ctx ($u, $suffix, $aa, $av, $fo, $join);
		if (isset ($fo["csv"]) || isset ($fo["xlsx"])) $aa["lim"] = "";
	}
	
	if ($id!==NULL)
	{ 
		$aa["w"]=" WHERE ".$t.".".$a[0][0]."=? "; 
		$aa["s"]="s"; 
		$av[]=$id; 
		if ($rights[$u][3]=="0" && ctx_rights ($u, $aa, $av, $p, $rights[$u])!=0) return 403; 	
		$aa_ = array ("ctx"=>"", "f"=>"", "w"=>"", "s"=>"", "sort"=>"", "lim"=>""); 
		$av_ = [];
		$fo_ = ["id"=>$id];
		$aa_["f"] = '"'.$u.$suffix.'_k":{';
		ctx_f ($u, $aa_, $av_, $fo_); // generate kmap only (no filters)
		$aa_["f"] .= '}';
		$aa["f"] = $aa_["f"];
	}
	
	if (isset ($fo["metrics"]))
	{ 
		return rpt ($u, $suffix, $fo, $aa, $av, $join); 
	}

	$aa['res'] = _select ($u, $aa, $av, "db", $join); 
	
	if ($aa['res']==NULL) return 500;
	
	if ($id!==NULL && isset ($fo["file"]))
	{
		return _file_download ($u, $aa, $fo["file"]); 
	}

	if ($id===NULL && isset ($fo["csv"]))
        {
                return _csv_download ($u, $aa['res'], $join); 
        }

	if ($id===NULL && isset ($fo["xlsx"]))
        {
                return _xlsx_download ($u, $aa['res'], $join); 
        }

	return 200;
}

function rest_uri_post ($u, $suffix, $id, &$o, &$p)
{
	error_log ("----------------------POST START (".$u.$suffix."/".$id.")-------------------------------------".$_SESSION["cc_user_role"]);
	//error_log ("  [o] ". json_encode ($o));
	//error_log ("  [p] ". json_encode ($p));
	
	if (!isset ($GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])])) return 403;
	$rights = $GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])];
	
	if (!isset ($GLOBALS[($u.$suffix."_api")])) return 404;

	$a = $GLOBALS[($u."_def")];
	$k = model_k_id ($u, $suffix, $a);
	
	$bb = $GLOBALS[($u.$suffix."_api")];
	$n = count ($bb);
	for ($i=0; $i<$n; $i++)
	{
		$b = $bb[$i];
		$a_ = $GLOBALS[($b[0]."_def")];
		$k_ = model_k_id ($b[0], $b[1], $a_);
error_log ("--->(".$b[2].")".$k_);		
		if ($b[2]=="aub")
		{
			if (isset ($p["aub_id"]) && strlen ($p["aub_id"])>0) continue;
			$q = "INSERT INTO aub(t) VALUES(?)";
			$argt = "s";
			$argv = [$b[0]];
			$aub_id = qryp ($q, $argt, $argv, 2);  // generate audit batch_id
			$p["aub_id"] = "".$aub_id;
			continue;
		}
		
		if ($b[2]=="lvl")
		{
			 _lvl ($b, $o, $p);
			continue;
		}
		
		if ($b[2]=="params")
		{
			 _params ($b, $o, $p);
			continue;
		}

		if ($b[2]=="dup" || $b[2]=="duf")
		{
			 _dup ($b, $o, $p);
			continue;
		}
		
		if (substr($b[2],0,3)=="agg")
		{
			_agg ($b, $o, $p);
			continue;
		}
		
		if ($b[2]=="include") 
		{
			$fm_=0;
			$bn = count ($b);
			if ($bn>3 && $b[3]=="1" && $id==NULL) $fm_=1; // allow link during add
			if ($bn>3 && $b[4]=="1" && $id!=NULL) $fm_=1; // allow link during upd
			if ($bn>3 && $fm_==0) continue;
			
			$rt_ = rest_uri_post ($b[0], $b[1], (isset($p[$k_])?$p[$k_]:NULL), $o, $p); // evaluate the full api scope
			if ($rt_==412) return 412;
			continue;
		}
		
		if ($b[2]=="object")
		{	
			if (!isset ($o[($b[0].$b[1])])) continue; 
			$o_ = $o[($b[0].$b[1])];
			$k_ = array_keys ($o_);
			$n_ = count ($k_);
			error_log ("[obj] ".$b[0].$b[1]."|".$n_."|".json_encode ($o_));
			if ($n_<1) continue; 
			for ($i_=0; $i_<$n_; $i_++) $o[$k_[$i_]] = $o_[$k_[$i_]]; // copy
			$rt_ = rest_uri_post ($b[0], $b[1], NULL, $o, $p);
			// error_log ("[obj] ".$b[0].$b[1]." copied |".$rt_."|".json_encode ($o)); 
			if ($rt_==412) return 412;
			continue;
		}
		
		if ($b[2]=="array")
		{	
			if (!isset ($o[($b[0].$b[1])])) continue; 
			$fm_ = 0;
			$bn = count ($b);
			if ($bn>3 && $b[3]=="1" && $id==NULL) $fm_=1; // allow link during add
			if ($bn>3 && $b[4]=="1" && $id!=NULL) $fm_=1; // allow link during upd
			if ($bn>3 && $fm_==0) continue;
		
			$p_ = [];
			$o_ = $o[($b[0].$b[1])];
			$n_ = count ($o_);
			error_log ("  [arr] ".$b[0].$b[1]."|".$n_);
			for ($i_=0; $i_<$n_; $i_++)
			{
				if (count (array_keys ($o_[$i_]))<1) {error_log ("empty!"); continue; } // skip empty object
				$o_[$i_]["i_"]=$i_;
				$p_ = $p; // error_log ("[arr] p: ".json_encode ($p_));
				$rt_ = rest_uri_post ($b[0], $b[1], NULL, $o_[$i_], $p_); 
				// if ($rt_==412) return 412;
			}
			// depricated // if ($bn>5 && $b[5]=="o") $p[$k_]=$p_[$k_]; // set id if array is marked as 'object'
			continue;
		}
		
		$t_ = $GLOBALS["RESOURCES"][$b[0]][0];
		$m_ = $GLOBALS["RESOURCES"][$b[0]][2];
		$s_ = "";	
		$id_ = NULL;
		if (isset ($o[$k_]) && strlen ($o[$k_])>0) $id_ = $o[$k_];
		if (isset ($p[$k_]) && strlen ($p[$k_])>0) $id_ = $p[$k_];
		
		if ($b[2]=="try")
		{
			$id_ = _try ($b[0], $b[1], $id_, $o, $p, $rights[$b[0]]);
			$s_ = "@ ";
		}
		
		if (strlen ($b[2])==0 && $id_!=NULL)
		{
			if ($m_!=2 && $m_!=3) continue;
			if ($rights[$b[0]][2]!="1") return 403; // check upd rights flag
			$fm_ = "2";
			if (isset ($b[3]))
			{
				if ($b[3]=="1" && $id!=NULL) continue; // skip if not in add mode
				$fm_ = $b[3];
			}
			error_log ("[upd] ".$b[0].$b[1]." | ".$k_."=".$id_." | ".$fm_);
			$id_ = _upd ($b[0], $b[1], $id_, $o, $p, $fm_);
			$s_ = "& ";
		}

		if (strlen ($b[2])==0 && $id_==NULL)
		{
			if ($m_!=1 && $m_!=3) continue;
			if ($rights[$b[0]][1]!="1") return 403; // check add rights flag
			if (isset ($b[3])) continue;		// skip -- b[3] flag not used for _add
			error_log ("[add] ".$b[0].$b[1]." | ".$k_);
			$id_ = _add ($b[0], $b[1], $o, $p);
			$s_ = "* ";
		}

		if ($b[2]=="file" && $id_==NULL)
		{
			if ($rights[$b[0]][1]!="1") return 403; // check add rights flag
			$p['batch_id'] = _val_id ();
			error_log ("[file] ".$b[0].$b[1]);
			if (!isset ($_FILES[$t_])) 
			{ 
				error_log (" --- no file to upload"); 
				_val_error ($u, $i, "File Format", "", "INVALID", "File Upload Failed!"); 
				return 412; 
			}
			$n_ = count ($_FILES[$t_]["name"]); // check for multiple files // nb: id_ = last file uploaded
			for ($i_=0; $i_<$n_; $i_++)
			{
				error_log ("  [file] ".$b[0].$b[1]."  ".$i_." of ".$n_);
				$o_ = array ();
				$o_["i_"]=$i_;				
				// $p_ = $p;
				$id_ = _file_upload ($b[0], $b[1], $o_, $p);
			}
			$s_ = "** ";
		}	

		error_log ("    +--".$s_.$k_."=".$id_);

		$p[$k_] = "".$id_;
		
		if ($id_==-2) return 412;		
	}

	error_log ("----------------------POST END (".$u.$suffix."/".$id.")-------------------------------------");

	if ($id!=NULL) return 202;
	
	return 201;
}

function rest_uri_parse ($meth, $uri, $i, &$u, &$suffix, &$id, &$o)
{
	if ($meth=="POST" && isset ($_SERVER["CONTENT_TYPE"]) && strstr ($_SERVER["CONTENT_TYPE"], "application/json")!=FALSE )
	{
		$s = file_get_contents ("php://input");
		$o = json_decode ($s, true);
		if ($o==NULL) return 400;
	}

	$id_ = NULL;
	$uri_ = explode ('?', $uri);
	$vv = explode ('/',$uri_[0]);
	$nn = count ($vv);
	if ($nn>0 && strlen ($vv[$nn-1])<1) $nn--; // skip last item if blank

	for ($i; $i<$nn; $i+=2)
	{
		$u = $vv[$i];
		$id_ = NULL;
		if ($i+1<$nn) $id_ = $vv[($i+1)];
		
		error_log ($u.",".$id_." |".$nn." | ".$i);

		if (strlen ($u)<1) return 404;
		$u = urldecode ($u);
		$uu = explode ('^', $u);
		$u = $uu[0];
		$suffix = "";
		if (count($uu)>1) $suffix = "_".$uu[1];
		// error_log ("---".$suffix);
		if (!isset ($GLOBALS[($u."_def")])) 
		{
			if (isset ($GLOBALS["FN"][$u])) break;
			return 404;
		}

		$t = $GLOBALS["RESOURCES"][$u][0];
		$ta = $GLOBALS["RESOURCES"][$u][1];
		if (strlen($ta)<1) $ta=$t;
		$a = $GLOBALS[($u."_def")];
		$n = count ($a);
		//$k = $ta."_".$a[0][0];
		//if (strlen ($a[0][1])>0) $k = $a[0][1];
		$k = model_k_id ($u, $suffix, $a);
		$o[$k] = $id_;
		if ($meth=="GET") $GET[$k] = $id_;
	}
			
	$id = $id_;

	return 0;
}

?>
