<?php
include "/var/www/html/helpline/config.php"; //

$db = mysqli_connect (THE_DB_HOST, THE_DB_USN, THE_DB_PASSWD, THE_DB_NAME, null, THE_DB_SOCK) or die ("Could Not connect to Database Server.");
$db2 = mysqli_connect (THE_DB_HOST, THE_DB_USN, THE_DB_PASSWD, THE_DB_NAME, null, THE_DB_SOCK) or die ("Could Not connect to Database Server.");

include "model.php";
include "model_k.php";
include "../lib/rest.php";
include "../lib/session.php";
include "../lib/XLSXbuf.php"; 
include "../lib/rpc.php"; 
//include "../lib/dialplan.php";

$FN = ["sendOTP"=>1, "verifyOTP"=>1, "resetAuth"=>1, "changeAuth"=>1, "dash"=>1, "wallonly"=>1, "agent"=>1, "chan"=>1, "sup"=>1, "msg"=>1, "msg_end"=>1, "eemis"=>1, "aii"=>1]; // non-crud endpoints

function copy_from_pabx ($uid) // copy from archive
{
	$url = $GLOBALS["RECORDING_ARCHIVE_URL"].$uid;
        $r = array ('data'=>'', 'info'=>0);
        $ch = curl_init ();
        curl_setopt ($ch, CURLOPT_URL, $url);
        curl_setopt ($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt ($ch, CURLOPT_TIMEOUT, 60);
//      curl_setopt ($ch, CURLOPT_VERBOSE, 2);
        $r['data'] = curl_exec ($ch);
        $r['info'] = curl_getinfo ($ch);
	error_log ("[copy_from_archive] ". $url." ".$r['info']['http_code']);
	if ($r['info']['http_code']==200)
	{
		header ("Content-Type: " . $r['info']['content_type']);
        	header ("Content-Length: " . strlen ($r['data']));
	        // header ('Content-Description: File Download');
        	header ('Content-Disposition: attachment; filename="'.$uid.'.ogg"');
	        // header ('Expires: 0');
        	header ('Cache-Control: no-cache');
	        // header ('Pragma: public');
	        header ("Content-Transfer-Encoding: binary");
		echo $r['data'];
		// error_log (json_encode ($r['info']));
		exit (0);
	}
}

function muu ($cmd, $args)
{
	$url = "http://127.0.0.1:8383/".$cmd."/".$args;
        $r = array ('data'=>'', 'info'=>0);
        $ch = curl_init ();
        curl_setopt ($ch, CURLOPT_URL, $url);
        curl_setopt ($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt ($ch, CURLOPT_TIMEOUT, 60);
//      curl_setopt ($ch, CURLOPT_VERBOSE, 2);
        $r['data'] = curl_exec ($ch);
        $r['info'] = curl_getinfo ($ch);
        curl_close ($ch);
        error_log ("[muu] ". $cmd."/".$args." | ".$r['info']['http_code']);
	// error_log ("[muu] >> ". $r['data']);
        return $r;
}

function muu_ ($cmd, $args) // nb: does not wait for response
{
	$sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	if (!$sock) {
    		error_log ("Failed to create socket: " . socket_strerror(socket_last_error()));
		return -1;
	}

	if (!socket_connect($sock, "127.0.0.1", "8383")) {
    		error_log ("Connection failed: " . socket_strerror(socket_last_error($socket)) );
		return -1;
	}
	
	$req = "GET /".$cmd."/".$args." HTTP/1.1\r\n\r\n";

	$ret = socket_write($sock, $req, strlen($req));

	error_log ("dont wait ------------".$ret);
}

function _aii (&$o, &$p)
{
	$s = file_get_contents('aii_demo.json'); // demo ai case output
	header ("HTTP/1.1 200 OK");
        header ('Content-Type: application/json');
	echo $s;
	return 200;
}

function national_registry (&$o, &$p)
{
	if (strlen($o["national_id_"])<1) return -1;
	$id=NULL;
	//$dup_ = array ("contacts","","dup","national_id","national_id_",NULL, "id"); // todo: use hidden field to match same contact everytime
	//_dup ($dup_, $o, $p);
	//if (isset($p["contact_id"])) $id=$p["contact_id"];
	error_log ("national_register: [o] ".json_encode($p));
	error_log ("national_register: [p] ".json_encode($o));
	$api_url = "https://backend.bitz-itc.com/api/webhook/eemis"; 
	$api_hdrs = ["Content-Type: application/json"];
	$api_body = "{ \"national_id\": \"".$o["national_id_"]."\" }";
	$r = kurl ($api_url, 60, $api_body, $api_hdrs);
	$a = json_decode ($r["data"], true);
	if ($a && isset($a["national_id"])) //  && isset($a["data"]) && isset($a["data"]["data"]))
	{
		$kk = array_keys ($a);
		$kn = count($kk);
		for ($i=0; $i<$kn; $i++) $o[("contact_".$kk[$i])] = $a[$kk[$i]];
		$o["contact_id"] = 0;
		$o["contact_fullname"] = $o["contact_lname"]." ".$o["contact_fname"];
		//rest_uri_post ("contacts","", $id, $a, $p); // create/update contact
		//if (isset($p["contact_id"])) 
		//{
		//	$id = $p["contact_id"];
		//	_dup ($GLOBALS["contacts_dup_api"][0], $o, $p);
		//}	
		$id=1;
	}
	return $id;
}

function message_out (&$o, &$p)
{
	$hdrs = array ("Content-Type: application/json");
	$postdata = array
	(
		"username"=>$GLOBALS["API_GATEWAY_USN"],
		"password"=>$GLOBALS["API_GATEWAY_PASS"]  
	);
	$token = ""; // kurl ($GLOBALS["API_GATEWAY_AUTH"], 60, json_encode($postdata), $hdrs);
	
	$api_url = $GLOBALS["API_GATEWAY_SEND_MSG"];
	$hdrs = array ("Content-Type: application/json");// , ("Authorization: Token ".json_decode($token["data"],true)["token"]));
	$postdata = array 
	(
		//"chat_sender"=>$o['src_address'], 
		//"chat_receiver"=>$p['src_usr'], 
		//"chat_message"=>$o['src_msg'], 
		//"chat_session"=>$o['src_callid'], 
		//"chat_channel"=> $o["src"],
		//"chat_source"=>"OUTBOX"//"HELPLINE"
		"recipient"=>$o['src_address'],
		"message_type"=>"text",
		"content"=>$o["src_msg"]
	);
	if (isset ($o["close"]))
	{
		$api_url = $GLOBALS["API_GATEWAY_CLOSE_MSG"].$o["src_callid"]."/close/";
		$postdata = array ("chat_source"=>"HELPLINE");
	}
	error_log ("[postdata] ".json_encode($postdata));
	kurl ($api_url, 60, json_encode($postdata), $hdrs);
	
	$s = "read?uid=".$o["src_uid2"]."&cid=".$o["src_usr"]."&";
	if (isset ($o["close"])) $s .= "args=close&"; // close session
        muu ("ati", $s); // update notification status
}

function _message_in (&$o, &$p)
{
	error_log ("   message_in -----". json_encode ($o));
	// curl -k "https://127.0.0.1/helpline/api/msg/" -H "Authorization: Bearer vd0ni7tps9la0fs6344mjikmt3" -H "Content-Type: application/json" -d '{"channel":"chat", "timestamp":"1680783378", "session_id":"1680783378", "message_id":"1680783378/00001", "from":"0700112233", "message":"how r u today?"}' -v
	$o_ = [];
	$o_['i_']=0;
	$o_["src"] = $o["channel"];
	$o_["src_uid"] = $o["message_id"]; 
	$o_["src_callid"] = $o["session_id"]; 
	$o_["src_address"] = $o["from"];
	$o_["src_msg"] = $o["message"];
	$o_["src_ts"] = $o["timestamp"];
	$o_["src_vector"] = "1";
	$o_['src_mime'] = $o["mime"];
        if ($o_['src']=='safepal') $o_['src_mime'] = "application/json";
	// $o_["gateway_msg_id"] = $o["message_id"];
	// $o_["gateway_session_id"] = $o["session_id"];
	$rt = rest_uri_post ("messages", "", NULL, $o_, $p);
	if ($rt==201) 
	{
		$msg = $o_["src_msg"];
		$msg = preg_replace ('/[[:^print:]]/', ' ', $msg); 
		$msg = str_replace ([' ', '&', '<', '>', "\r","\n","\t"], ['_', '', '', '', '', '', ''], $msg); 
		if (strlen ($msg)>30) $msg = substr ($msg,0,30)."..."; // trunccate to fit in notif 
		// $s = "msg?src=".$o_['src']."&address=".$o_['src_address']."&id=".$o_['src_uid']."&msg=".$msg."&";
		$s = "msg?ctx=".$o_['src']."&cid=".$o_['src_address']."&chan=".$o_['src_callid']."&payload=".$msg."&";
		if ($o_["src"]=="aii") $s .= "exten=*&"; // dont agtk!
		muu ("ati", $s); // post to notif_queue

		$aa = [];
		$fo = [];
		$rt = rest_uri_get ("messages", "", $p["msg_id"], $fo, $p, $aa);
		if ($rt==200)
		{
			return rest_uri_response ("messages", "", $p["msg_id"], $o, $p, $aa, 201);
		}
	}
	error_log (" msg rt=".$rt." | ". json_encode ($p));
	return $rt;
}

function _sup (&$o) // "action=", "exten="
{
	$usn = $_SESSION["cc_user_usn"];
	$exten = $_SESSION["cc_user_exten"];
	$role = $_SESSION["cc_user_role"];

	error_log ("[sup] request ".json_encode ($o)." | ".$usn. " ". $exten);
	
	if ($role!=2 && $role!=99) return 404;
	
	$r = muu ("ami","sync?c=-1&");
	$o_ = json_decode ($r['data'], true);
	$k = array_keys ($o_['channels']);
	$n = count ($k);
	$me = null;
	$agent = null;
	for ($i=0; $i<$n; $i++) 
	{
		$ch = $o_['channels'][$k[$i]];
		if (strlen ($ch[16])>0) continue;
		if ($me===null && $ch[4]==$exten && $ch[5]=="Supervisor") //substr($ch[43],0,10)=="supervisor") 
		{ 
			$me=$k[$i]; 
			continue; 
		}
		if ($agent===null && isset ($o["exten"]) && $ch[0]==$o["exten"]) // find agent uid
		{
			$agent=$k[$i];
			continue;
		}
	}
	$s = "sup?action=".$o['action']."&usr=".$usn."&exten=".$exten;
	if (isset ($o["exten"])) $s .= "&agent=".$o['exten'];
	if ($me!=null) $s .= "&chan=".$o_['channels'][$me][3];
	if ($agent!=null) $s .= "&uid=".$agent;
	muu ("ami",$s); 
	header ("HTTP/1.0 203 Wait");
	header ('Content-Type: application/json');
	$ts = time ();
	echo '{ "action":[["'.$ts.'","'.$o['action'].'"]] }'; 
	return 201;
}

function _chan (&$o)
{
	$usn = $_SESSION["cc_user_usn"];
	$exten = $_SESSION["cc_user_exten"];
	
	error_log ("[chan] request ".json_encode ($o)." | ".$usn. " ". $exten);
	
	if ($o['action']>2 && $o['action']<6) // cb_xfer, cb_conference, cb_resume
	{
		$s = "redirect?action=".$o['action']."&exten=".$o['exten']."&chan1=".$o['chan']."&chan3=".$o['chan3']."&";
		muu ("ami",$s); 
	}

	if ($o['action']>0 && $o['action']<3) // cb_invite, cb_dial
	{
		if (!isset ($o['add'])) $o['add']='';
			
		if (isset ($o['usn_']))
		{
			$o['add'] = $o['usn_'];
		}
		
		if (isset ($o['user_id']))
		{
			$row = qryp ("SELECT exten FROM auth WHERE id=?", "s", [$o['user_id']], 1);
			if ($row)  $o['add'] = $row[0];
		}
		
		if (strlen ($o['add'])!=3 || !is_numeric ($o['add'])) // validate exten
		{
			header ("HTTP/1.0 412 Wait");
			header ('Content-Type: application/json');
			echo '{ "errors":[["error","Invalid Extension"]] }'; 
			return 413;
		}
	
		$o['exten'] = 'CB'.$o['src_uid'];
		if (isset ($o['cbid']) && strlen ($o['cbid'])>0) { $o['exten'] = $o['cbid']; $o['chan2'] = ''; } // dont redirect peer already in bridge
		if (!isset ($o['chan2'])) $o['chan2'] = '';
		$s = "redirect?action=".$o['action']."&usr=".$o['usr']."&exten=".$o['exten']."&chan1=".$o['chan']."&chan2=".$o['chan2']."&add=".$o['add']."&ref=".$o['src_address']."&";
		muu ("ami", $s); 
	}
	
	if ($o['action']==0)
	{
		$s = "hangup?chan=".$o['chan3']."&";
		muu ("ami", $s); 
	}

	$ts = time ();
	$add = '';
	if (isset ($o['add'])) $add = $o['add'];
	header ("HTTP/1.0 203 Wait");
	header ('Content-Type: application/json');
	echo '{ "action":[["'.$ts.'","'.$o['action'].'","'.$add.'"]] }'; 
	return 202;
}

function _agent (&$o)
{
	$usn = $_SESSION["cc_user_usn"];
	$exten = $_SESSION["cc_user_exten"];
	$role = $_SESSION["cc_user_role"];

	error_log ("[agent] request ".json_encode ($o)." | ".$usn. " ". $exten);

	if ($o['action']=='0') // get chan id
	{
		$r = muu ("ati","sync?c=-1&");
		$o_ = json_decode ($r['data'], true);
		$k = array_keys ($o_['ati']);
		$n = count ($k);
		$me = null;
		for ($i=0; $i<$n; $i++) if ($o_['ati'][$k[$i]][0]==$exten) { $me=$k[$i]; break; }
		$s = "leave?uid=".$me."&";
		if ($me!=null) muu ("ati",$s); 
		if ($me==null) error_log (" * [ati agent not found ] ");

		$r = muu ("ami","sync?c=-1&");
		$o_ = json_decode ($r['data'], true);
		$k = array_keys ($o_['channels']);
		$n = count ($k);
		$me = null;
		for ($i=0; $i<$n; $i++) if ($o_['channels'][$k[$i]][0]==$exten) { $me=$k[$i]; break; }
		$s = "usr?action=0&call_id=".$me."&";
		if ($me!=null) muu ("ami",$s); 
		if ($me==null) error_log (" * [ami agent not found ] ");
	}

	if ($o['action']=='1')
	{
		$k = ['any','sun','mon','tue','wed','thu','fri','sat'];
		$q = "SELECT UNIX_TIMESTAMP(Date(Now())), Dayofweek(Now())";
		$row = qryp ($q, "", [], 1);
		$at = [];
		$av = [$row[0], $row[0], _S('cc_user_id')];	
		$q = "SELECT workinghour.campaign_id, campaign_campaign FROM workinghour INNER JOIN member ON workinghour.campaign_id=member.campaign_id && source='1' && dt0<=? && dt1>=? && ".$k[$row[1]]."='1' && user_id=?";  // fetch active campaigns
		$res = qryp ($q, "sss", $av, 0);
		$campaigns = "";
		$outbound = 0;
		while ($row = mysqli_fetch_row ($res))
		{
			error_log ("MBR: [".$row[0]." ".$row[1]."]");
			$v = $row[0];
			if ($row[1]==2) { $v="O"; $outbound++; }
			if ($outbound>1) continue;
			$campaigns .= $v.",";
		}
		if ($campaigns=="") $campaigns = "0,";

		// if ($role==6) // login to ati only
		{
			$s = "join?cid=".$exten."&";
			muu ("ati",$s); 
			// $campaigns = "Z,";
			$campaigns .= "Z,";
		}

		$s = "usr?action=1&usr=".$exten."&interface=2&exten=".$GLOBALS['VA_SIP_USER_PREFIX'].$exten."&queue=".$campaigns."&";
		muu ("ami",$s); 

	}
	
	if ($o['action']=='4') // enable auto answer
	{
		$s = "usr?action=4&usr=".$exten."&";
		muu ("ami",$s); 
	}
	
	if ($o['action']=='5') // disable auto answer
	{
		$s = "usr?action=5&usr=".$exten."&";
		muu ("ami",$s); 
	}

	return 203;
}

function _wallonly (&$o, &$p)
{
	muu_ ("rpt",""); // sync stats from rpt // rpty ();

        if (isset ($_GET["metrics"]))
        {
                if (isset ($_GET["dash_period"]))
                {
                         $_GET["dt"] = _str2ts ("today");
                       //  muu ("rpt",""); // sync stats from rpt // rpty ();
                }

		header("HTTP/1.1 200");
		header ('Content-Type: application/json');
		echo '{';

		$_SESSION["cc_user_role"] = "2";
		$aa = [];
		$av = [];
		$fo = $_GET;
		$rt = rest_uri_get ("calls", "", NULL, $fo, $p, $aa);
		if ($rt==200)
		{
			rest_uri_response ("calls", "", NULL, $o, $p, $aa, 0);
		}

		echo ', "stats":{ ';


		$q = "SELECT UNIX_TIMESTAMP(Date(Now())) dt, UNIX_TIMESTAMP(CONCAT(YEAR(Now()),'-',MONTH(Now()),'-01')) mn";
                $row = qryp ($q, "", $av, 1);
		$dt_now = $row[0];
		$mn_now = $row[1];

		$q = "SELECT COUNT(id) FROM kase WHERE dt=?";
		$av_ = [$dt_now];
                $row = qryp ($q, "s", $av_, 1);
                echo '"cases_today":"'.$row[0].'",';

		$q = "SELECT COUNT(id) FROM kase WHERE status=2";
		$av_ = [$mn_now];
                $row = qryp ($q, "", $av, 1);
                echo '"cases_closed_this_month":"'.$row[0].'",'; 

		$q = "SELECT COUNT(id) FROM kase WHERE status=1";
		$row = qryp ($q, "", $av, 1);
                echo '"cases_ongoing_total":"'.$row[0].'",';

                $q = "SELECT COUNT(id) FROM kase";
                $row = qryp ($q, "", $av, 1);
                echo '"cases_total":"'.$row[0].'",';

		$q = "SELECT COUNT(id) FROM chan WHERE dt=?";
                $av_ = [$dt_now];
                $row = qryp ($q, "s", $av_, 1);
                echo '"calls_today":"'.$row[0].'",';

		$q = "SELECT COUNT(id) FROM chan";
                $av_ = [$dt_now];
                $row = qryp ($q, "", $av, 1);
                echo '"calls_total":"'.$row[0].'"';

/*
		$q = "SELECT hangup_status, has_case_id, count(hangup_status) FROM chan WHERE hangup_status=5 GROUP BY hangup_status, has_case_id";
		$res = qryp ($q, "sss", $av, 0);
		while ($row = mysqli_fetch_row ($res))
		{
                	echo '"has_case_id_'.$row[1].'":"'.$row[2].'",';
		}
		
		$q = "SELECT hangup_status, has_case_id, count(hangup_status) FROM chan WHERE dt=? && hangup_status=5 && has_case_id='1'";
		$av_ = [$dt_now];
                $row = qryp ($q, "s", $av_, 1);
                echo '"responsive_calls_today":"'.$row[2].'"';
 */
                echo '}';

                echo '}';
                return 200;
        }

	if (isset ($_GET["stats"]))
	{
		// $q = "SELECT SUM(if(hangup_status_txt='answered',1,0)), SUM(if(hangup_reason='phone' and vector=2 and hangup_status<5 ,1,0)), SUM(talk_time) FROM chani WHERE dt=? AND usr=?";
		$q = "SELECT SUM(if(hangup_status_txt='answered',1,0)), SUM(if(hangup_status<5 && peer_hangup!='1',1,0)), SUM(if(hangup_status_txt='answered',src_status_duration,0)) FROM activity WHERE dt=? AND src_usr=? && src='call' && src_vector='2'";
		$_GET["dt"] = _str2ts ("today");
		$av = [__VESC(_G("dt")), __VESC(_G("exten"))];
        	$row = qryp ($q, "ss", $av, 1);
		echo '{ "stats":[';
		if ($row) echo '["'.$row[0].'","'.$row[1].'","'.$row[2].'"]';
		echo ']}'; 
		return 200;
	}

        $q = "SELECT id, usn, exten, role FROM auth WHERE exten=?";
        $av = [__VESC(_G("exten"))];
        $row = qryp ($q, "s", $av, 1);
        header("HTTP/1.0 200 OK");
        header ('Content-Type: application/json');
        echo '{ "users":[["'.$row[0].'","'.$row[1].'"]] }';
        return 200;
}

function _dash (&$o, &$p)
{
	$rights = $GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])];
	$dash_period = "this_month";
	$dash_gbv = "both";
	$dash_src = "all";
	if (isset ($_GET["dash_period"])) $dash_period = $_GET["dash_period"];
	if (isset ($_GET["dash_gbv"])) $dash_gbv = $_GET["dash_gbv"];
	if (isset ($_GET["dash_src"])) $dash_src = $_GET["dash_src"];

	$_gbv_ = array ("both"=>"", "vac"=>"0", "gbv"=>"1" );	
	$_src_ = array ("all"=>"", "call"=>"call", "sms"=>"sms", "email"=>"email", "social"=>"social", "walkin"=>"walkin" );
	$dash_ts = _str2ts ($dash_period);
	
	echo '"dash":[["'.$dash_period.'","'.$dash_gbv.'","'.$dash_src.'","'.$dash_ts.'","'.$_gbv_[$dash_gbv].'","'.$_src_[$dash_src].'"]]';
		
	$aa = array ("ctx"=>"", "f"=>"", "w"=>"", "s"=>"", "sort"=>"", "lim"=>"");
	$av = [];
	ctx_rights ("cases", $aa, $av, $p, $rights["cases"]);
	if (strlen ($_gbv_[$dash_gbv])>0) k_c ("kase", "gbv_related", explode (",", $_gbv_[$dash_gbv]), $aa, $av);
	if (strlen ($dash_ts)>0) 	  k_d ("kase", "created_on", explode (";", $dash_ts), $aa, $av);
	$q = "SELECT src, COUNT(id) FROM kase ".$aa["w"]." GROUP BY src";
	error_log ("[dash] ".$q." | ".json_encode ($av)." | ".$_SESSION["cc_user_role"]);
	$res = qryp ($q, $aa["s"], $av);
	$i = 0;
	$tot = 0;
	echo ',"case_source":{';
	while ($row = mysqli_fetch_row ($res))
	{
		if ($i>0) echo ","; 
		echo '"'.$row[0].'":["'.$row[0].'","'.$row[1].' Cases"]';
		$i++;
		if ($row[0] && strlen ($row[0])>0) $tot += $row[1]; 
	}
	if ($i>0) echo ","; 
	echo '"total":["total","'.$tot.' Cases"]}';
	return 200;
}

function _home (&$o, &$p)
{
	if (!isset ($GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])])) return 403;
	$rights = $GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])];
	$aa = [];
	$fo = [];
		
        header ("HTTP/1.0 200 OK");
	header ('Content-Type: application/json');
        echo "{";
       
	ss ();
	
	echo ",";
	if (rest_uri_get ("auth","", $p["auth_id"], $fo, $p, $aa)==200) rest_uri_response ("auth","", $p["auth_id"], $o, $p, $aa, 0);
        	
	echo ",";
	if (rest_uri_get ("contacts","", "0", $fo, $p, $aa)==200) rest_uri_response ("contacts","", "0", $o, $p, $aa, 0); // load contacts_k
	
	echo ",";
	if (rest_uri_get ("categories","", "-9", $fo, $p, $aa)==200) rest_uri_response ("categories","", "-9", $o, $p, $aa, 0);

       	echo ",";
	if (rest_uri_get ("cases","", "0", $fo, $p, $aa)==200) rest_uri_response ("cases","", "0", $o, $p, $aa, 0); // also load case_subs

	echo ",";
	if (rest_uri_get ("messages","", "0", $fo, $p, $aa)==200) rest_uri_response ("messages","", "0", $o, $p, $aa, 0); // load messages_k

	//echo ",";
	//if (rest_uri_get ("qas","", "0", $fo, $p, $aa)==200) rest_uri_response ("qas","", "0", $o, $p, $aa, 0); // load qas_k

	echo ",";
	if (rest_uri_get ("dispositions","", "0", $fo, $p, $aa)==200) rest_uri_response ("dispositions","", "0", $o, $p, $aa, 0); // load dispositions_k
	
	echo ",";
	$fo_=["_c"=>"10"];
	if (rest_uri_get ("activities","", NULL, $fo_, $p, $aa)==200) rest_uri_response ("activities","", NULL, $o, $p, $aa, 0); // load activities

	echo ","; 
	$fo_ = ["_c"=>"1000", "root_id"=>$GLOBALS["AGE_GROUP_ROOT_ID"] ];
	if (rest_uri_get ("categories","_age_group", NULL, $fo_, $p, $aa)==200) rest_uri_response ("categories","_age_group", NULL, $o, $p, $aa, 0);
		
	//$q = "SELECT GROUP_CONCAT(DISTINCT campaign_id) FROM workinghour WHERE dt0<=unix_timestamp(date(now())) && dt1>=unix_timestamp(date(now()))";
	//$av = [];
	//$row = qryp ($q, "", $av, 1);
	//$active_campaigns = "0";
	//if ($row && strlen ($row[0])>0) $active_campaigns=$row[0];
	//$fo_=["id"=>$active_campaigns];
	//error_log ("ACTIVE CAMPAIGNS: ".$active_campaigns);
	//echo ",";
	//if (rest_uri_get ("campaigns","", NULL, $fo, $p, $aa)==200) rest_uri_response ("campaigns","", NULL, $o, $p, $aa, 0);
	
	//$q = "SELECT GROUP_CONCAT(DISTINCT user_id) FROM shift WHERE dt0<=unix_timestamp(date(now())) && dt1>=unix_timestamp(date(now()))";
	//$av = [];
	//$row = qryp ($q, "", $av, 1);
	//$active_users = "0";
	//if ($row && strlen ($row[0])>0) $active_users=$row[0];
	//$fo=["_c"=>"1000"]; // ["id"=>$active_users];
	//error_log ("ACTIVE USERS: ".$active_users);
	//echo ",";
	//if (rest_uri_get ("users","", NULL, $fo, $p, $aa)==200) rest_uri_response ("users","", NULL, $o, $p, $aa, 0);
	
	echo ",";
	_dash ($o, $p);

        echo "}";
        return 200;
}

function _request_ ()
{
	$u = "";
	$suffix = "";
	$id = NULL;
	$o = [];
	$p = [];
	$fo = [];

	error_log ("[auth] ".$_SERVER["REQUEST_URI"]);

	$rt = rest_uri_parse ($_SERVER["REQUEST_METHOD"], $_SERVER["REQUEST_URI"], 3, $u, $suffix, $id, $o);
	if ($rt!=0) return $rt;
	
	if ($u=="wallonly") return _wallonly ($o, $p);

	if ($u=="sendOTP") return _sendOTP ($o,$p);

	if ($u=="verifyOTP") return _verifyOTP ($o,$p); // onverify creates a 'temp' session to allow password reset

	if (isset ($_GET["logout"]))
	{
		$o_ = ["action"=>"0"]; // remove member from queue(s)
		_agent ($o_);
	}
	
	$rt = auth ($o);

	if ($rt!=0) return $rt;

	error_log ("auth (".$u.$suffix.") ---------------------------------------------------------|"._S("cc_user_usn"));	
	$p["auth_id"] = _S("cc_user_id");
	$p["auth_exten"] = _S("cc_user_exten");
	$p["auth_usn"] = _S("cc_user_usn");
	$p["profile_id"] = _S("cc_user_contact_id"); 
	$p["auth_is_active"] = "1";
		
	if (strlen($u)<1) return _home ($o,$p);

	if ($u=="resetAuth") return changeAuthAdmin ($id);
	
	if ($u=="changeAuth") return changeAuth ($o, $p);
	
	if ($u=="agent") return _agent ($o);
	
	if ($u=="chan") return _chan ($o);
	
	if ($u=="sup") return _sup ($o);
	
	if ($u=="dash") 
	{
		echo '{';
		_dash ($o, $p);
		echo '}';
		return 200;
	}
	
	if ($u=="msg") return _message_in ($o, $p);

	if ($u=="aii") return _aii ($o, $p);

	if ($_SERVER["REQUEST_METHOD"]=="GET") 
	{
		$fo = $_GET;
		$rt = 200;
		if ($id=="-1") $o = $fo;
	
		if ($u=="calls" && isset ($_GET["dash_period"])) 
		{
			error_log ("dash ----|".json_encode ($_GET));
			$_GET["dt"] = _str2ts ("today");
			// muu ("rpt",""); // sync stats from rpt // rpty ();
		}
	
		if ($u=="cases") // eval _title
		{
			$_t = _G ("_title");
			if ($_t=="my_cases") $fo["created_by_id__i"] = $p["auth_id"]; // my cases 
			if ($_t=="esca_by_me") $fo["escalated_by_id__i"] = $p["auth_id"]; // esca_by_me
			if ($_t=="esca_to_me") $fo["escalated_to_id__i"] = $p["auth_id"]; // esca_to_me
			if ($_t=="all_cases_today") { $fo["created_on__i"] = strtotime(date("d F Y")); }
		
			$case_count_yaxis = ["today"=>["hour","line"], "this_week"=>["dt","line"], "this_month"=>["dt","line"], "last_3_month"=>["mn","line"], "last_6_month"=>["mn","line"], "last_9_month"=>["mn","line"], "this_year"=>["mn","line"], "all"=>["yr","bar"] ];
			if (isset ($_GET["yaxis"]) && $_GET["yaxis"]=="dt" && isset ($_GET["dash_period"]))
			{
				error_log ("rpt? ".$_GET["yaxis"]." | ".$_GET["dash_period"]);
				$fo["yaxis"] = $case_count_yaxis[$_GET["dash_period"]][0];
				$fo["type"] = $case_count_yaxis[$_GET["dash_period"]][1];
			}
		}

		if ($u=="activities" && $suffix=="_case" && $id=="-1" && isset($o["src_msg"])) {$o["case_id"] = explode ("-", $o["src_msg"])[1];}
	}
		
	if ($_SERVER["REQUEST_METHOD"]=="POST")
	{
		if ($u=="reporters") 
		{
			if ($id!=NULL) { $o["activity"]="9"; }; 
		}
			
		if ($u=="clients" && $id==NULL) { $o["activity"]="6"; }	
		if ($u=="perpetrators" && $id==NULL) { $o["activity"]="7"; }
		if ($u=="attachments" && $id==NULL) { $o["activity"]="8"; }			

		if ($u=="clients" && $id!=NULL) { $o["activity"]="10"; }
		if ($u=="perpetrators" && $id!=NULL) { $o["activity"]="11"; }
		if ($u=="attachments" && $id!=NULL) { $o["activity"]="12"; }	
		
		if ($u=="clients" && $id!=NULL && isset ($o['is_delete'])) { $o["activity"]="13"; }
		if ($u=="perpetrators" && $id!=NULL && isset ($o['is_delete'])) { $o["activity"]="14"; }
		if ($u=="attachments" && $id!=NULL && isset ($o['is_delete'])) { $o["activity"]="15"; }
	
		if ($u=="cases") 
		{
			$o["activity"]="1"; 
			if ($id!=NULL)
			{
				$o["activity"]="2"; 
				if (isset ($o["case_category_id"])) $o["activity"]="3"; 

				if (isset ($o["escalated_to_id"]))
				{
					$dup_ = array ("cases","","dup","id","case_id",NULL, "escalated_to_id:escalated_to_id");
					$o_ = ["case_id"=>$id, "escalated_to_id"=>$o["escalated_to_id"]];
					$p_ = [];
					_dup ($dup_, $o_, $p_); 
					if ($o["escalated_to_id"]==$p_["escalated_to_id"])
					{ 
						unset ($o["escalated_to_id"]); // unset escalated_to if no change
					}
					if (isset ($o["escalated_to_id"]) && $o["escalated_to_id"]=="0")
					{
						$o["escalated_to"] = "";
						$o["escalated_to_role"] = "";
					}
					

					// escalated_to same but escalated_by diff
				}
			}
			
			if ($id==NULL) $o['assigned_to_id'] = $p['auth_id']; 		
			if (isset ($o["escalated_to_id"])) $o['escalated_by_id'] = $p['auth_id'];
		}
		
		if ($u=="messages") // outgoing msgs
		{
			$tv = gettimeofday ();
			$p["src_vector"] = "2";
			$p["src_usr"] = $_SESSION["cc_user_exten"];
			//$p["gateway_session_id"] = $o["src_uid"];
			//$p["gateway_msg_id"] = $o["src"]."-".$tv["sec"]."-".$tv["usec"]; 
		}

		if ($u=="clients" && isset($o["national_id_"]))
		{
			$aa = [];
			$id = national_registry($o, $p);
			echo "{";
			if ($id>0)
			{
				error_log ("[national reg]".json_encode($o));
				rest_uri_response ("clients", "", "-1", $o, $p, $aa, 0);
			}
			echo "}";
			return 200;
		}
					
		$o['i_']=0;
		$rt = rest_uri_post ($u, $suffix, $id, $o, $p);

		$a_ = $GLOBALS[($u."_def")];
		$k = model_k_id ($u, $suffix, $a_);
		$id = "-2";
		if (($rt==201 || $rt==202) && isset ($p[$k])) $id = $p[$k];
		error_log ("rt-->".$rt." ".$k);

		// todo: increase wrapup to 5minutes on case_uuid // todo convert case_uuid GETs to PUTs				
		if (($u=="cases" || $u=="dispositions") && $rt>200 && $rt<203 && isset ($o["src"]) && $o["src"]=="call") // shrink wrapup to 20 seconds on save
                {
			$s = "wrapup?action=0&usr=".$_SESSION["cc_user_exten"];
                        $r = muu ("ami","sync?c=-1&");
                        $o_ = json_decode ($r['data'], true);
			if (isset ($o_["channels"]) && isset ($o["src_uid"]) && isset ($o_["channels"][$o["src_uid"]]))  // get chan.uid (if rxists)
			{
				$s .= "&chan=".$o_["channels"][$o["src_uid"]][3]."&";
			}
			muu ("ami",$s);
                }
                
                if ($rt==201 && $u=="messages")
                {
                        message_out ($o, $p);
                }
		
		if ($rt==201 && $u=="cases" && isset ($p["escalated_to_id"]) && $p["escalated_to_id"]>0)
		{
			//_notify ("msg?", "escalation", "", $p["auth_usn"], $p["escalated_to_exten"], ($GLOBALS["CASE_ID_PREFIX"].$p["case_id"]), "1", 0);
			// notify ("escalation", $p["escalated_to_id"], $o, $p);
		}
		
		if ($rt==202 && $u=="cases" && isset ($p["escalated_to_id"]) && $p["escalated_to_id"]>0)
		{
			$q = "SELECT id FROM au WHERE aub_id=? && row_id=? && t=? && k=?"; // query aub if escalated_to has changed
			$av = [$p["aub_id"], $p["case_id"], "cases", "escalated_to_id"];
			$r = qryp ($q, "ssss", $av, 1);
			error_log ("[escanb] ".json_encode ($av));
			// notify ("escalation", $p["escalated_to_id"], $o, $p);
			//if ($r) _notify ("msg?", "escalation", "", $p["auth_usn"], $p["escalated_to_exten"], ($GLOBALS["CASE_ID_PREFIX"].$p["case_id"]), "1", 0); 
		}

		if ($u=="cases" && $rt>200 && $rt<203)
		{
			error_log ("PHP - ".$p["case_id"].", ".$p["dsp_id"].", ".$p["ca_id"]);
			muu_ ("sync",""); // wakeup sync
		}
	}
	
	if ($rt==200 || $rt==201 || $rt==202)
	{
		error_log ("get-->".$rt." ".$id." | ".json_encode ($fo));
		$rt_ = $rt;
		$aa = [];
		$rt = rest_uri_get ($u, $suffix, $id, $fo, $p, $aa);
		if ($rt==200) 
		{
			$rt = rest_uri_response ($u, $suffix, $id, $o, $p, $aa, $rt_);
			//if ($u=="activities" && $id==-1 && $o["src"]=="escalation") // onview close notif
			//{
			//	//_notify ("close?", $o["src"], $o["src_uid"], $o["src_address"], $p["auth_exten"], "close", "2", 0); 
			//}
		}
	}
	
	return $rt;
}

session_set_save_handler ("ss_open", "ss_close", "ss_read", "ss_write", "ss_destroy", "ss_gc");
session_name ("HELPLINE_SESSION_ID");
session_start ();

$rt = _request_ ();
if ($rt>299) rest_uri_response_error ($rt);
if ($rt==203)
{
	header ("HTTP/1.0 203 Wait");
	header ('Content-Type: application/json');
	echo '{ "action":[["notice","async"]] }'; 
}

?>