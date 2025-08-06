<?php
include "/var/www/html/test/config.php"; //

$db = mysqli_connect (null, "voiceapps", null, THE_DB_NAME, null, THE_DB_SOCK) or die ("Could Not connect to Database Server.");
$db2 = mysqli_connect (null, "voiceapps",  null, THE_DB_NAME, null, THE_DB_SOCK) or die ("Could Not connect to Database Server.");

include "/var/www/html/test/api/model.php";
include "/var/www/html/test/api/model_k.php";
include "/var/www/html/test/lib/rest.php";
include "/var/www/html/test/lib/session.php";
include "/var/www/html/test/lib/rpc.php";

function model_k ($u, $suffix)
{
	$a = $GLOBALS[($u."_def")];
        $t = $GLOBALS["RESOURCES"][$u][0];
        $ta = $GLOBALS["RESOURCES"][$u][1];
        if (strlen($ta)<1) $ta=$t;
        $k = $ta.$suffix."_".$a[0][0];
        if (strlen ($a[0][1])>0) $k = $a[0][1].$suffix;
        return $k;
}

function kv ($k, &$op, &$o, &$p)
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


// dup, params, val

function jo (&$a, $an, &$row, &$s)
{
        for ($j=0; $j<$an; $j++)
        {
		if ($j>0) $s .= ",\r\n";
		$k=$a[$j][0];
		if (strlen ($a[$j][1])>0) $k = $a[$j][1];
                $s .= '"'.$k.'":"'.$row[$j].'"';
        }
}

function fk (&$a, $an, &$row, &$p)
{
        for ($j=1; $j<$an; $j++)  // collect fk
        {
                $v=$row[$j];
                if ($a[$j][3]!='2') continue;
                $p[$a[$j][0]] = $v;
                error_log ("[fk] ".$j." : ".$a[$j][0]." = ".$v);
        }
}

function arg ($t, $k, $v, &$o, &$p, &$aa, &$av)
{
	$w=" WHERE ";
	$op = "=";
	$v_ = _kv ($v, $op, $o, $p);
	if ($v_!==NULL)
	{
		$w = " WHERE ";
		if ($strlen($aa["w"])>0) $w = " && ";
		$aa["w"] .= $w.$b[$i]." ".$op."?";
		$aa["s"] .= "s";
		$av[] = $v_;
	}
	return $v_;
}

// todo: arg_s,arg_n,arg_ch,arg_ft,arg_d 

function arg_c ($t, $k, $v, &$o, &$p, &$aa, &$av)
{
	$s = ' WHERE ';
	if (strlen ($aa["w"])>0) $s = ' && ';
	$n = count ($v);
	$c = 0;
	for ($j=0; $j<$n; $j++) if (strlen($v[$j])>0)
	{
		if ($c==0) $aa["w"] .= $s.$t.'.'.$k." IN (";
		if ($c>0) $aa["w"] .=",";
		$aa["w"] .= "?";
		$aa["s"] .= "s";
		$av[] = $v[$j];
		$c++;
        }
        if ($c>0) $aa["w"] .= ")";
}

function args (&$b, &$o, &$p, &$aa, &$av)
{
	$e=0;
        $n = count ($b);
        for ($i=3; $i<$n; $i+=2)
	{
		if ($b[$i]===NULL) break; // end also on NULL
		$v = arg ($b[$i], $b[($i+1)], $o, $p, $aa, $av);
		if ($v===NULL)
        	{
                        $e++;
                        error_log ("[arg] (".$b[0].$b[1].")  ".$k." isnull ");
                }
	}
	return $e;
}

function args_uri ($u, $suffix, $id, &$o, &$aa, &$av) // replacement for ctx_f
{
	if ($id!==NULL)
	{
		$aa["w"] = " WHERE id=? ";
		$aa["s"] = "s";
		$av[] = $id;
		return 0;
	}
	$e=0;
	$p=[];
	$t = $GLOBALS["RESOURCES"][$u];
	$a = $GLOBALS[($u."_def")];
        $an = count ($a);
	for ($j=0; $j<$an; $j++)
	{
		$m = $a[$j][3];
		$k = $a[$j][0];
		$v = NULL;
		if (strlen($a[$j][1])>0) $k=$a[$j][1];  // alias
		if (isset ($o[$k])) $v = $o[$k];
		if (strlen ($v)<1) continue;
		if ($m==2) arg_c ($t[0], $k, explode (",",$v), $o, $p, $aa, $av);
	}
	return $e;
}

function uri_response_error ()
{

}

function uri_response ($u, $suffix, $id, &$o, &$s)
{
	$p = [];
	$a = $GLOBALS[($u."_def")];
	$an = count ($a);
	$aa = ["w"=>"", "sort"=>"", "lim"=>"", "s"=>""];
	$av = []; 
	args_uri ($u, $suffix, $id, $o, $aa, $av);
	$res = _select ($u, $aa, $av);
        if ($res==NULL) return -1;
	$row = mysqli_fetch_row ($res);
	if ($row==NULL) return -2;  // eof
	$k = model_k ($u, $suffix);
	$p[$k] = $row[0];
	jo ($a, $an, $row, $s);

	if ($id===NULL)
	{
		while (($row = mysqli_fetch_row ($res))) // next rows
		{
			$s .='},{';
			jo ($a, $an, $row, $s);
		}
		return 0;
	}

	fk ($a, $an, $row, $p);
//	error_log (json_encode ($p));
	$bb = $GLOBALS[($u.$suffix."_subs")]; // subs
	$bn = count ($bb);
	for ($i=0; $i<$bn; $i++)
	{
		$b = $bb[$i];
		$s .= ",\r\n".'"'.$b[0].$b[1].'":';
		$s .= $b[2]=='o' ? '{' : '[';
		$id_ = NULL;
		$o_ = [];
		// todo: check model_id match -> set id for more recursion
		$e = 0;
        	$jn = count ($b);
		for ($j=3; $j<$jn; $j+=2)
        	{
			$op = "=";
        		$v_ = _kv ($b[($j+1)], $op, $o, $p);
			if ($v_===NULL) 
			{
				$e++;
				error_log ("[sub] (".$b[0].$b[1].")  ".$b[($j+1)]." isnull ");
				continue;
			}
			$o_[$b[$j]] = $v_;
		}
		if ($e==0) uri_response ($b[0], $b[1], $id_, $o_, $s);
		$s .= $b[2]=='o' ? '}' : ']';
	}
	return 0;
}

function uri_post ()
{

}

function uri ()
{
	// parse
	// uri_post ()
	// uri_response ();
}

// ---------------------------------------

$cases_ceemis_subs =
[
//["reporters","_uuid","",     "id","reporter_uuid_id"],
// ["reporters","","o",	"id","reporter_id"],
//["perpetrators","_case","",  "case_id_","case_ceemis_id"],
//["clients","_case","",       "case_id_","case_ceemis_id"],
// ["attachments","_case","",   "case_id_","case_ceemis_id"],
//["services","","",	"case_id_","case_ceemis_id"],
//["referals","","",  	"case_id_","case_ceemis_id"]
];

function case_sync (&$caid)
{
	$aa = ["w"=> ("WHERE case_dept=1 && activity IN (1,2,3) && syncts=0 && id>".$caid), "sort"=>"ORDER BY id", "lim"=>"LIMIT 1", "s"=>"" ];
	$av = [];
        $res = _select ("case_activities", $aa, $av);
        if ($res==NULL) return -1;
	$row = mysqli_fetch_row ($res);
	if ($row==NULL) return -2;   	// eof
	$case_activities_k = $GLOBALS["case_activities_k"];
	$p["case_id"] = $row[$case_activities_k["case_id"]];
	$p["ca_id"] = "".$row[0];
	$caid = $row[0];

	error_log ("[sync] --- ".json_encode ($p));

	$aa = ["w"=>"WHERE id=?", "sort"=>"", "lim"=>"", "s"=>"s" ];
        $av = [$p["case_id"]];
        $res = _select ("cases", $aa, $av);
	if ($res==NULL) return -1;
	$row = mysqli_fetch_row ($res);
	if ($row==NULL) return -2;      // eof
	$cases_k = $GLOBALS["cases_k"];
	//error_log (json_encode($cases_k));
	$p["case_ref"] = $row[$cases_k["ref"]];
	// return;

	// todo get max case_activity with current case_id
	$o = [];
	$s = "{";
	uri_response ("cases","_ceemis",$p["case_id"],$o,$s);	
	if (strlen ($p["case_ref"])>0) $s .= ",\"ref\":\"".$p["case_ref"]."\"";
	$s .= "}";

error_log ($s);

	$api_url = "https://backend.bitz-itc.com/api/webhook/helpline/case/ceemis/";
	$api_opts = [];
	if (strlen ($p["case_ref"])>0)
	{
		$api_url .= "update/"; // .$p["case_ref"]."/";
		$api_opts = [CURLOPT_CUSTOMREQUEST => 'PUT'];
	}
	$api_hdrs = ["Content-Type: application/json"];
	$r = kurl ($api_url, 60, $s, $api_hdrs, $api_opts);
	if ($r['info']['http_code']!=200) return -1;
	$o_ = json_decode ($r['data'], true);
	if (!$o_) return -1;

	if ($o_["status"]=="success" && $o_["ceemis_response"]["status"]==true)
	{
		$_SESSION["cc_user_role"] = "99";
		error_log ("CEEMIS: ".$p["ca_id"]."/".$o_["ceemis_response"]["msg"]."---------------------");
		$p__ = [ "ca_id" => $p["ca_id"] ];
		$o__ = [ "syncts" => ("".time()) ];
		if (strlen ($p["case_ref"])<1) $o__["theirref"] = $o_["ceemis_response"]["msg"];
		rest_uri_post ("case_activities", "_sync", $p["ca_id"], $o__, $p__);
		return 0; // uri_post (); // update case_activities with sync ts
	}


	//header ("HTTP/1.0 200 OK");
	//header ('Content-Type: application/json');
	//echo $s;
	//echo $r["data"];
	return -1;
}
$rt=0;
$caid=0;
while ($rt!=-2)
{
	$rt = case_sync ($caid);
	error_log ("[sync-return] ".$rt." ".$caid."---------------------------");
}

?>
