<?php
/*
Transcribe audio after end of a call recording and post the result to CRM
*/

// curl -X POST http://192.168.10.6:11434/api/generate -H "Content-Type: application/json" --data @mistral.json

define('FIFOPATH','/var/spool/asterisk/monitor/123456789.wav');
define('APIURL','http://192.168.10.6:8000/api/core/upload/');
define('FFMPEGCMD','/mnt/recovery/usr/local/bin/ffmpeg -f s16le -ar 8000 -ac 1 -i pipe:0 -ar 16000 -ac 1 -f wav pipe:1');

function io ()
{ 
	$fifo = fopen(FIFOPATH, 'rb');
	if (!$fifo) 
	{
		error_log ("Failed to open namedpipe for reading.\n");
		return -1;
	}
	error_log ("connected to asterisk sucessfully at fifo:".FIFOPATH);
	$data = stream_get_contents($fifo);
	if ($data === false || trim($data) === '') 	// Avoid empty reads 
	{
		error_log ("empty reading.");
		return -1;
	}
	error_log (strlen($data)." bytes read");
	$descriptors = 
	[
		0 => ['pipe', 'r'],  // stdin
    		1 => ['pipe', 'w'],  // stdout
		2 => ['pipe', 'w'],  // stderr
	];
	$process = proc_open (FFMPEGCMD, $descriptors, $pipes);
	if (!is_resource($process)) 
	{
    		error_log("Failed to start FFmpeg process");
		return -1;
	}
	$w = fwrite($pipes[0], $data);
	error_log ($w." bytes wriiten to ffmpeg");
	fclose($pipes[0]); 				// Important: close stdin so FFmpeg knows input has ended
	$outputWav = stream_get_contents($pipes[1]); 	// Read the output WAV data from FFmpeg's stdout
	fclose($pipes[1]);
	$stderr = stream_get_contents($pipes[2]);	// Optionally read any error output (for debugging)
	fclose($pipes[2]);
	$returnCode = proc_close($process);		// Close FFmpeg process
	if ($returnCode !== 0) 
	{
    		error_log("FFmpeg error:".$stderr);
    		return -1;
	}
	error_log ("Transcribing ".strlen($outputWav)." bytes of 16KHz wav file");
	$apitimeout=3600;
	// $apihdrs = ["Content-Type: multipart/form-data"];
	$dataUri = 'data://audio/wav;base64,' . base64_encode($outputWav);
	$cfile = new CURLFile($dataUri, 'audio/wav', 'a.wav');
	$postFields = [ 'audio' => $cfile ];
	$r = array ('data'=>'', 'info'=>0);
	$ch = curl_init ();
        curl_setopt ($ch, CURLOPT_URL, APIURL);
        curl_setopt ($ch, CURLOPT_HEADER, false);
        curl_setopt ($ch, CURLOPT_RETURNTRANSFER, true);
	
	curl_setopt ($ch, CURLOPT_VERBOSE, true);
        $log = fopen('/tmp/transcribe_curl_debug.log', 'w');
	curl_setopt($ch, CURLOPT_STDERR, $log);

	curl_setopt ($ch, CURLOPT_TIMEOUT, $apitimeout);
    	// curl_setopt ($ch, CURLOPT_HTTPHEADER, $apihdrs);
	curl_setopt ($ch, CURLOPT_POST, true);
	curl_setopt ($ch, CURLOPT_POSTFIELDS, $postFields);
	$r['data'] = curl_exec ($ch);
        $r['info'] = curl_getinfo ($ch);
        error_log ("[curl_info] ". $r['info']['http_code'] ."|".json_encode ($r['info']));
        error_log ("[curl_result] ".$r['info']['http_code']." | ". $r['data']);

	fclose ($log);
        curl_close ($ch);
	// todo: POST response to CRM
}

while (1) 
io();

?>
