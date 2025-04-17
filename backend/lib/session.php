<?php

function ss_id ($id)
{
	// error_log ("SESSION ID: ".$id." | ".$_SERVER["HTTP_AUTHORIZATION"]);

	if (isset ($_SERVER["HTTP_AUTHORIZATION"])) 
	{
		$vv = explode (" ",$_SERVER["HTTP_AUTHORIZATION"]);
		if (strcasecmp ($vv[0], "bearer")==0) 
		{
			//error_log ("SESSION AUTH: BEARER ".$vv[1]." |".$id);
			return $vv[1];
		}
	}
	return session_id (); // get php session-id
}

function ss_open ($path, $name)
{
	// error_log ("SESSION OPEN: ".$path." ".$name);
	return true;
}

function ss_close ()
{
	// error_log ("SESSION CLOSE: ");
	return true;
}

function ss_read ($id)
{
	//b error_log ("SESSION READ: ");
	$id = ss_id ($id);
	$q = "SELECT data FROM session WHERE ss_id=?";
	$argv = [$id];
	$row = qryp ($q, "s", $argv, 1);
	if ($row)
	{
		// error_log ("SESSION READ: ".$id." |". $row[0	]);
		$vv = explode ("|",$row[0]);	
		$_SESSION["cc_user_id"] = $vv[0];
		$_SESSION["cc_user_usn"] = $vv[1];
		$_SESSION["cc_user_agentno"] = $vv[2];
		$_SESSION["cc_user_exten"] = $vv[3];
		$_SESSION["cc_user_contact_id"] = $vv[4];
		$_SESSION["cc_user_role"] = $vv[5];
		$q = "UPDATE session SET access=UNIX_TIMESTAMP(Now()) WHERE ss_id=?";
		qryp ($q,"s",$argv, 4);
	}
	return "";
}

function ss_write ($id, $data)
{
//	error_log ("SESSION WRITE: ".$id." |".$data);
	return true;
}

function ss_del ($row)
{
	$user_id = $row[3];

	$o = [];
	//ami_leaveq ($o, $_SESSION['cc_user_agentno'], "1");

	error_log ("SESSION del sessid=".$row[1]."--------------");
	$q = 'INSERT INTO session_log(created_on, ss_action, ss_start, ss_end, ss_id, ss_ip, user_id, user_usn, user_role, data, access) VALUES(UNIX_TIMESTAMP(Now()),"ss_del",?,UNIX_TIMESTAMP(Now()),?,?,?,?,?,?,?)';
	$argv = array ($row[0], $row[1], $_SERVER["REMOTE_ADDR"], $row[3], $row[4], $row[5], $row[6], $row[7]);
	qryp ($q, "ssssssss", $argv, 2);
	$q = "DELETE FROM session WHERE ss_id=?";
	$argv = array ($row[1]);
	qryp ($q, "s", $argv, 3);
	return true;
}

function ss_destroy ($id)
{
	error_log ("SESSION DESTROY: ".$id);
	$q = "SELECT created_on, ss_id, ss_ip, user_id, user_usn, user_role, data, access FROM session WHERE ss_id=?";
	$argv = [$id];
	$row = qryp ($q,"s",$argv,1,"db2");
	if ($row) ss_del ($row);
	return true;
}

function ss_gc ($n)
{
	error_log ("SESSION GC: ".$n); // // logout after 5 minutes of inactivity
	$q = "SELECT created_on, ss_id, ss_ip, user_id, user_usn, user_role, data FROM session WHERE UNIX_TIMESTAMP(Now())-access>36000"; 
	$argv = [];
	$res = qryp ($q,"",$argv,0,"db2");
	if (!$res) return true;
	$row = mysqli_fetch_row ($res);
	while ($row)
	{
		ss_del ($row);
		$row = mysqli_fetch_row ($res);
	}
	return true;
}

function ss_new ($row) // id, usn, agentno, exten, contact_id, contact_role
{
	error_log ("SESSION NEW regen--------------");
	session_regenerate_id (true);

	$id = session_id ();
	error_log ("SESSION ss_new=".$id."---------------");
	$s = $row[0]."|".$row[1]."|".$row[2]."|".$row[3]."|".$row[4]."|".$row[5]."|";
	$_SESSION["cc_user_id"] = $row[0];
	$_SESSION["cc_user_usn"] = $row[1];
	$_SESSION["cc_user_agentno"] = $row[2];
	$_SESSION["cc_user_exten"] = $row[3];
	$_SESSION["cc_user_contact_id"] = $row[4];
	$_SESSION["cc_user_role"] = $row[5];

	$q = 'INSERT INTO session(created_on, access, ss_id, ss_ip, user_id, user_usn, user_role, data) VALUES(UNIX_TIMESTAMP(Now()),UNIX_TIMESTAMP(Now()),?,?,?,?,?,?)';
	$argv = array ($id, $_SERVER["REMOTE_ADDR"], $row[0], $row[1], $row[5], $s);
	qryp ($q, "ssssss", $argv, 2);

	$q = 'INSERT INTO session_log(created_on, ss_action, ss_start, ss_id, ss_ip, user_id, user_usn, user_role, data) VALUES(UNIX_TIMESTAMP(Now()),"ss_new",UNIX_TIMESTAMP(Now()),?,?,?,?,?,?)';
	qryp ($q, "ssssss", $argv, 2);
}

function ss_new_phone ($otp_id, $addr_id, $addr, $role)
{
	error_log ("SESSION regen-pre--------------");
	session_regenerate_id (true);

	$id = session_id ();
	$s = 'cc_otp_id|s:'.strlen($otp_id).':"'.$otp_id.'";';
	$s .= 'cc_addr_id|s:'.strlen($addr_id).':"'.$addr_id.'";';
	$s .= 'cc_addr|s:'.strlen($addr).':"'.$addr.'";';
	error_log ("SESSION new sessid (reset)=".$id." | ".$s);
	$q = 'INSERT INTO session(created_on, access, ss_id, ss_ip, user_usn, user_role, data) VALUES(UNIX_TIMESTAMP(Now()),UNIX_TIMESTAMP(Now()),?,?,?,?,?)';
	$argv = array ($id, $_SERVER["REMOTE_ADDR"], $addr, $role, $s);
	qryp ($q, "sssss", $argv, 2);
	$q = 'INSERT INTO session_log(created_on, ss_action, ss_start, ss_id, ss_ip, user_usn, user_role, data) VALUES(UNIX_TIMESTAMP(Now()),"ss_new",UNIX_TIMESTAMP(Now()),?,?,?,?,?)';
	qryp ($q, "sssss", $argv, 2);
}

session_set_save_handler ("ss_open", "ss_close", "ss_read", "ss_write", "ss_destroy", "ss_gc");
session_name ("HELPLINE_SESSION_ID");
session_start ();

function ss ()
{
	$ssid = ss_id("");
	echo '"ss":[["'.$ssid.'"';
	if (isset ($_SESSION["cc_user_id"])) 
	{
		echo ',"'.$_SESSION["cc_user_id"].'", "'.$_SESSION["cc_user_usn"].'", "'.$_SESSION["cc_user_role"].'","'.$_SESSION["cc_user_contact_id"].'"'; //
	}
	echo ']]'; 
}

function _sendOTP (&$o,&$p) 
{
	$o["now"] = time(); // seconds
	$o["otp"] = _rands (8,"num");
	$o["expiry"] = time()+600; // seconds
	$o["email"] = $o["addr"];

	if (_val_email ($o["addr"])==1)
	{
		_val_error ("auth",0,"addr",$o["addr"],"INVALID","Invalid Email Address");
		return 412;
	}

	_dup ($GLOBALS["addr_dup"], $o, $p);
	_dup ($GLOBALS["otp_dup"], $o, $p);
	_dup ($GLOBALS["auth_dup"], $o, $p);

	if (!isset ($p['addr_id'])) // collect address
	{	
		$p['addr_id'] = _add ("addr", "addr", $o, $p); 
	}

	if (!isset ($p['auth_id'])) // check if registered // disable depending on onboarding flow
	{	
		_val_error ("auth",0,"addr","","INVALID","No Account Registered with that Email Address");
		return 412;
	}

	$p['otp_id'] = _add ("otp", "otp", $o, $p); 

	if ($p['otp_id']<1)
	{
		_val_error ("auth",0,"addr",$o["addr"],"ERROR","An Error Occured please try again later");
		return 412;
	}
	
	$o['email'] = $o['addr'];
	_dup ($GLOBALS["contacts_dup"], $o, $p);
	$p['_email'] = '<'.$p['contact_email'].'>';
	$p['email_id'] = send_email ("EMAIL_OTP", $o, $p);

	header ("HTTP/1.0 201 OK");
	header ('Content-Type: application/json');
	echo '{"auth_nb":[["info","OTP sent to '.__VESC($o["addr"]).'"]], "addr":[["'.__VESC($o["addr"]).'"]]}';
	return 201;
}

function _verifyOTP (&$o,&$p)
{
	$o["now"] = time (); // seconds
	_dup ($GLOBALS["otpv_dup"], $o, $p);
	$p["email"] = $p["otp_addr"];
	_dup ($GLOBALS["auth_dup"], $o, $p);
	
	if (!isset ($p["otp_id"]) || !isset ($p["email"]))
	{
		_val_error ("auth",0,"addr","","ERROR","Invalid OTP Code");
		return 412;
	}
	
	ss_new_phone ($p['otp_id'], $p['otp_addr_id'], $p['otp_addr'], $p['auth_contact_role']);

	header ("HTTP/1.0 201 OK");
	header ('Content-Type: application/json');
        echo "{";
        ss ();
	echo ",\"auth_nb\":[[\"info\",\"OTP Verified Successfuly\"]]";
        echo "}";
	return 201;
}

function resetAuth (&$o, &$p, $e) // if post verify (auto create session)
{
		
	//$o["otp_id"] = $_SESSION["cc_otp_id"];
	//	$o["addr_id"] = $_SESSION["cc_addr_id"];
	//	$o["addr"] = $_SESSION["cc_addr"];
	//	$p["usn"] = $_SESSION["cc_addr"];
	//	$o["email"] = $_SESSION["cc_addr"];
		
	if (!isset ($o["pass1"]))
	{
		$e += _val_error ("auth",0,"addr",$o["addr"],"INVALID","Password is blank");
	}

	if ($o["pass1"]!=$o["pass2"])
	{
		$e += _val_error ("auth",0,"addr",$o["addr"],"INVALID","Passwords Do no match");
	}

	if (strlen ($o["pass1"])<8)
	{
		$e += _val_error ("auth",0,"addr",$o["addr"],"INVALID","Password Must be 8 or more characters");
	}

	if ($e>0) return $e;
	
	_dup ($GLOBALS["contacts_dup"], $o, $p);
	_dup ($GLOBALS["auth_dup"], $o, $p);
 
	// if self register 
	if (!isset ($p['contact_id'])) // create contact if does not exist
	{
		$o["role"] = "1"; // 1:default (0=inactive)
		$id = _add ("contacts", "", $o, $p);
		if ($id<1) return 412;
		$p['contact_id']=$id;
		_dup ($GLOBALS["contacts_dup"], $o, $p);
	}

	// if self register 
	if (!isset ($p['auth_id'])) // register if does not exist
	{
		$o["usn"] = $o["addr"];
		$id = _add ("users", "", $o, $p);
		if ($id<1) return 412;
		$p['auth_id']=$id;
		_dup ($GLOBALS["auth_dup"], $o, $p);
	}
	
	if (!isset ($p['auth_id']) || !isset ($p['contact_id']))
	{ 
		return _val_error ("auth",0,"addr",$o["addr"],"ERROR","An Error Occured please try again later");
	}

	
	ss_destroy (ss_id ()); // delete this session (one time use only)

	$hash = hash ("sha256", $o["pass1"]);
	$chat_id = hash ("sha256", ($o['addr'].$p['contact_id'])); 
	$q = "UPDATE auth SET pass=?, agentno=? WHERE id=?";
	$argv = array ($hash, $chat_id, $p["auth_id"]);
	qryp ($q,"sss",$argv,3);
	

	header ("HTTP/1.0 202 Updated");
	header ('Content-Type: application/json');
	echo '{"auth_nb":[["info","Password Reset Successfuly"]]}';        
	
	return 202;
}

function changeAuth (&$o, &$p)
{
	$e = 0;

	if (!isset ($o["pass1"]))
	{
		$e += _val_error ("auth",0,"addr",($o["addr"]),"INVALID","Password is blank");
	}

	if ($o["pass1"]!=$o["pass2"])
	{
		$e += _val_error ("auth",0,"addr",($o["addr"]),"INVALID","Passwords Do no match");
	}

	if (strlen ($o["pass1"])<8)
	{
		$e += _val_error ("auth",0,"addr",($o["addr"]),"INVALID","Password Must be 8 or more characters");
	}

	$pass = hash ("sha256", $o["pass0"]); 	
	$argv = array ($_SESSION["cc_user_id"], $pass);
	$row = qryp ("SELECT id FROM auth WHERE id=? AND pass=?","ss",$argv,1);
	if ($row==NULL)
	{
		$e += _val_error ("auth",0,"pass0","","INVALID","That is not your current password.");
	}

	if ($e>0) return 412;

	$newpass = hash ("sha256", $o["pass1"]); 
	$q = "UPDATE auth SET pass=? WHERE id=? AND pass=?";
	$argv = array ($newpass, $_SESSION["cc_user_id"], $pass);
	$af = qryp ($q,"sss",$argv,3);

	error_log ("changeAUth SESSION ".$af." |". json_encode ($argv));

	$s = "Password Changed";
	if ($af<1) $s = "New Password same as Old Password";

	$u = "profile";
	$aa = [];
	$o_ = array ();
	$fo_ = [];
	$rights = $GLOBALS[("RIGHTS_".$_SESSION["cc_user_role"])];
	// $rt = rest_uri_get ("profile", $p["profile_id"], $o_, $p, 202, $rights, $fo_);
	$rt = rest_uri_get ("auth", "", $_SESSION["cc_user_id"], $fo_, $p, $aa);
	if ($rt==200) 
	{
		return rest_uri_response ("auth", "", $_SESSION["cc_user_id"], $o_, $p, $aa, 202);
	}
	
	_val_error ("auth",0,"pass0","","INVALID","System error! password change failed.");	
	return 412;
}

function changeAuthAdmin ($user_id)
{
	error_log (" SESSION [changeAuthAdmin] ".$_SESSION["cc_user_role"]."-------------- |".$user_id);
	
	$e = 0;
	
	if ($_SESSION["cc_user_role"]!="99")
	{
		$e += _val_error ("auth",0,"role","","INVALID","Only Admin can reset password.");
		return 412;
	}
	
	$newpass = _rands (8,"num"); // generate random pass
	$newhash = hash ("sha256", $newpass); 
	$q = "UPDATE auth SET pass=?, updated_on=UNIX_TIMESTAMP(Now()) WHERE id=?"; // todo flag as one time pass
	$argv = array ($newhash, $user_id);
	$af = qryp ($q,"ss",$argv,3);
	error_log ($_SESSION["cc_user_role"]."----SESSION ----------".$af." |".$user_id);
	if ($af>0) 
	{
		header ("HTTP/1.0 202 OK");
		header ('Content-Type: application/json');
        	echo '{"auth_nb":[["info","Password Reset Successful. The new password is '.$newpass.'"]]}';
		return 202;
	}
	$e += _val_error ("auth",0,"role","","INVALID","Password Reset failed. Contact Admin!.");
	return 412;
}

function auth ($o)
{
	$auth = [];

	if (isset ($_GET["logout"]))
	{
		error_log ("SESSION LOGOUT ".session_id ());
		$_SESSION = array ();
		session_destroy ();
		return 401;
	}

	if (isset ($_SERVER["HTTP_AUTHORIZATION"])) 
	{
		$vv = explode (" ",$_SERVER["HTTP_AUTHORIZATION"]);

		if (strcasecmp ($vv[0], "basic")==0) 
		{
			$a = base64_decode ($vv[1], TRUE);
			if ($a) 
			{
				$aa = explode (":",$a);
				$auth["auth_u"] = $aa[0];
				$auth["auth_p"] = $aa[1];
				// error_log ("AUTH: BASIC: ".json_encode ($auth));
			}
		}
	}

	if (isset ($auth["auth_u"]))
	{
                $usn = $auth["auth_u"];
                $pass = hash ("sha256", $auth["auth_p"]); 
		// $q = "SELECT id, usn, agentno, exten, contact_id, role FROM auth WHERE usn=? AND pass=?";
                $q = "SELECT id, usn, agentno, exten, contact_id, role FROM auth WHERE is_active='1' AND usn=? AND pass=?";
                $argv = [$usn, $pass];
		$row = qryp ($q, "ss", $argv, 1);  
                if ($row==NULL)
                {
                	_val_error ("auth", 0, "login", $usn, "REQUIRED", "Invalid Username or Password!");
                        return 412; // invalid username or password
                }
		ss_new ($row);
	}

	if (isset ($_SESSION["cc_user_id"]))
	{
		return 0; 
	}

	return 401; // Authentication Required
}

?>
