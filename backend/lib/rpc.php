<?php

/* NICE TO HAVE CURL OPTS

	curl_setopt ($ch, CURLINFO_HEADER_OUT, true);
	curl_setopt ($ch, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt ($ch, CURLOPT_SSL_VERIFYHOST, 0);
	curl_setopt ($ch, CURLOPT_STDERR, $fd);
	curl_setopt($ch,CURLOPT_ENCODING, '');

*/

/* KURL SEND EMAIL
	$fp = fopen ($filename, 'c+');
	$opts = [ // CURLOPT_URL => ,
	CURLOPT_MAIL_FROM => '',
	CURLOPT_MAIL_RCPT => [$p['_email']],
	CURLOPT_USERNAME => '',
	CURLOPT_PASSWORD => '',
	CURLOPT_USE_SSL => CURLUSESSL_ALL,
//	CURLOPT_READFUNCTION => 'read_cb',
	CURLOPT_INFILE => $fp,  // file handle // 
	CURLOPT_UPLOAD => true ];
	$r = kurl ('', null, null, $opts);
	close 
*/

function kurl ($url,$timeout,$postdata=null,$hdrs=null,$opts=null,$email_to=null,$email_content=null)
{
	$fp = null;
        $r = array ('data'=>'', 'info'=>0);
        $ch = curl_init ();
        curl_setopt ($ch, CURLOPT_URL, $url);
	curl_setopt ($ch, CURLOPT_HEADER, false);
        curl_setopt ($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt ($ch, CURLOPT_TIMEOUT, $timeout);
        // curl_setopt ($ch, CURLOPT_VERBOSE, 2);
	if ($opts!=null)
	{
		curl_setopt_array ($ch, $opts);
	}
	if ($hdrs!=NULL && count ($hdrs)>0)
	{
		curl_setopt ($ch, CURLOPT_HTTPHEADER, $hdrs);
	}
	if ($postdata!=null)
	{
		curl_setopt($ch, CURLOPT_POST, true);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata); 
	}
	if ($email_to!=null) // send email via curl
	{
		$fp = fopen ($email_content, 'r');
		curl_setopt ($ch, CURLOPT_MAIL_FROM, $GLOBALS['SMTP_FROM_ADDRESS']);
		curl_setopt ($ch, CURLOPT_MAIL_RCPT, $email_to);
		curl_setopt ($ch, CURLOPT_USERNAME, $GLOBALS['SMTP_AUTH_USN']);
		curl_setopt ($ch, CURLOPT_PASSWORD, $GLOBALS['SMTP_AUTH_PASS']);
		curl_setopt ($ch, CURLOPT_USE_SSL, CURLUSESSL_ALL);
		//	CURLOPT_READFUNCTION => 'read_cb',
		curl_setopt ($ch, CURLOPT_INFILE, $fp);  // file handle // 
		curl_setopt ($ch, CURLOPT_UPLOAD, true);
	}
        $r['data'] = curl_exec ($ch);
        $r['info'] = curl_getinfo ($ch);
        curl_close ($ch);
	if ($fp!=null) fclose ($fp);
	// error_log ("[curl_info] ". $r['info']['http_code'] ."|".json_encode ($r['info']));
	error_log ("[curl_result] ".$r['info']['http_code']." | ". $r['data']);
        return $r;
}

// function api_response () { } // maps 3rd party response to system

// function api_request () { } // maps system params to 3rdparty request

// todo: 3rd party model // 
// usage: 
//  api_request (); 
//  kurl (); 
//  api_response ()

?>
