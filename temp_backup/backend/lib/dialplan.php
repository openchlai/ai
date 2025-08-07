<?php

/* queues_custom.conf

[queue_0]
autofill=yes 
joinempty=no
leavewhenempty=yes
ringinuse=no
reportholdtime = no
;monitor-type = MixMonitor
;monitor-format = wav
context=prompt_inqueue
musicclass = queue_moh
strategy = rrmemory
wrapuptime = 40
timeout = 20
retry = 2 ; wait 2 seconds before retry all again
announce-holdtime = once
announce-position = yes
announce-frequency = 60
queue-thankyou=
periodic-announce-frequency=90
periodic-announce = voiceapps/all_agent_are_busy

[prompt_invalid]
exten => s, 1, Set(Q_E=$[${Q_E}+1])
exten => s, n, GotoIf($["${Q_V}"="0"]?${Q_PROMPT},s,4)
exten => s, n, GotoIf($["${Q_V}"="8"]?prompt_16,s,1) ;main menu
exten => s, n, GotoIf($["${Q_V}"="9"]?${Q_PROMPT_PARENT},s,1) ;previous menu
;exten => s, n, Read(Q_W,"invalid",1,,1,1)
exten => s, n, GotoIf($["${Q_E}"<"3"]?prompt_${Q_PROMPT},s,4)
;exten => s, n, Playback(goodbye)
exten => s, n, Hangup

[prompt_blank]
exten => s, 1, Set(Q_E=$[${Q_E}+1])
;exten => s, n, Read(Q_W,"invalid",1,,1,1)
exten => s, n, GotoIf($["${Q_E}"<"3"]?prompt_${Q_PROMPT},s,4)
;exten => s, n, Playback(goodbye)
exten => s, n, Hangup

*/

/*
rk["voiceprompt_type"] = ["1","2","3","4","5","6","7"];
re["voiceprompt_type"] = 
{
"":["","",			"",		"leaf",		"branch_footer","leaf", 	"noop","noop","noop-noop-ve-type"],
"0":["0","-",			"-",		"leaf",		"branch_footer","leaf", 	"noop","noop","noop-noop-ve-type"],
"1":["1","Playback",       	"Playback",  	"voiceprompt_r_branch",		"voicemap_rr_btn","voicemap_r_branch", 	"noop","noop","noop-noop-ve-type"],
"2":["2","Menu",		"Menu",		"voiceprompt_r_branch",		"voicemap_rr_btn","voicemap_r_branch", 	"noop","noop","noop-noop-ve-type"],
"3":["3","Capture Digits",	"DTMF",		"leaf", 	"branch_footer","leaf", 	"voiceprompt_vw_dtmf","voiceprompt_ed_dtmf","voiceprompt_ed_dtmf-voiceprompt_-ve-type"],  
"4":["4","Capture Voice",	"Record",	"leaf",		"branch_footer","leaf", 	"voiceprompt_vw_record","voiceprompt_ed_record","voiceprompt_ed_record-voiceprompt_-ve-type"], 
"5":["5","Dial Extension",	"Exten",	"leaf",		"branch_footer","leaf", 	"voiceprompt_vw_extension","voiceprompt_ed_extension","voiceprompt_ed_extension-voiceprompt_-ve-type"],
"6":["6","Dial Campaign Users",	"Queue",	"leaf",		"branch_footer","leaf", 	"noop","noop","noop-noop-ve-type"],  
"7":["7","Invoke API",		"API",		"voiceprompt_r_branch", 	"voicemap_rr_btn","voicemap_r_branch", 	"voiceprompt_vw_api","voiceprompt_ed_api","voiceprompt_ed_api-voiceprompt_-ve-type"] 
};
*/

define('VOICEPROMPT_PLAYBACK', '1');
define('VOICEPROMPT_MENU', '2');
define('VOICEPROMPT_CAPTURE_DTMF', '3');
define('VOICEPROMPT_CAPTURE_VOICE', '4');
define('VOICEPROMPT_EXTEN', '5');
define('VOICEPROMPT_AGENTS', '6');
define('VOICEPROMPT_API', '7');

// #include /home/dat/voiceapps/conf/*.conf

// ------------------------------------------------

function rsync ()
{

}

// ------------------------------------------------

function queue_moh ($row, $fd)
{
	$s = "[queue_moh_".$row[0]."]\r\n";
	$s .= "mode=playlist\r\n";
	$q = "SELECT id, file_id FROM moh WHERE source_id=? ORDER BY pos ASC";
	$av = [$row[0]];
	$res = qryp ($q, "s", $av, 0, "db2");
	// error_log ("queue_moh_".$row[0]."----------------------------------------------------------------------------");
	while (($row_ = mysqli_fetch_row ($res))) // copy vfiles
	{
		$s .= "entry=/home/dat/voiceapps/vfiles/".$row_[1]."\r\n";
	}
	$s .= "\r\n";
	fwrite ($fd, $s);
}

function queue_params ($row, $fd)
{
	$s = "[queue_".$row[0]."]\r\n";
	$s .= "autofill=yes\r\n"; 
	$s .= "joinempty=yes\r\n";
	$s .= "leavewhenempty=no\r\n";
	$s .= "ringinuse=no\r\n";
	$s .= "reportholdtime = yes\r\n";
	$s .= "monitor-type = MixMonitor\r\n";
	$s .= "monitor-format = gsm\r\n";
	$s .= "musicclass = queue_moh_".$row[0]."\r\n";
	$s .= "strategy = rrmemory\r\n";
	$s .= "timeout = ".$row[2]."\r\n";
	// $s .= "wrapuptime = ".$row[3]."\r\n";
	$s .= "wrapuptime = 2\r\n";
	$s .= "retry = 5\r\n";
	$s .= "announce-holdtime = once\r\n";
	$s .= "announce-position = yes\r\n";
	$s .= "announce-frequency = 90\r\n";
	$s .= "\r\n";
	fwrite ($fd, $s);
}

function queue_conf ($campaign_id)
{
	$fdn = DAT."/conf/queue_".$campaign_id.".conf"; 
	$fdn_moh = DAT."/conf/moh_".$campaign_id.".conf"; 
	$q = "SELECT id, agent_ring_strategy, agent_ring_timeout, agent_wrapup, campaign FROM campaign WHERE id=?"; 
	$row = qryp ($q, "s", [$campaign_id], 1); 
	if ($row && $row[4]==1)
	{
		$fd = fopen ($fdn, 'w'); 
		$fd_moh = fopen ($fdn_moh, 'w'); 
		queue_params ($row, $fd);
		queue_moh ($row, $fd_moh);
		fclose ($fd);
		fclose ($fd_moh);
	}
	rsync ();
	ami ("reload?");
	ami ("whr?");
}

// ------------------------------------------------

function dialplan_prompt ($row, $fd)
{
	$read_var = "Q_V";
	$read_max_digits = "1";
	$read_timeout = 1;
	if ($row[2]==VOICEPROMPT_MENU) { $read_timeout = 10; } // menu timeout
	if ($row[2]==VOICEPROMPT_CAPTURE_DTMF) { $read_timeout = 10; $read_max_digits=$row[6]; } // key capture timeout
	if ($row[2]==VOICEPROMPT_CAPTURE_VOICE) { $read_timeout = $row[7]; } // voice capture timeout

	$s = "[prompt_".$row[0]."]\r\n";
	$s .= "exten => s, 1, Answer\r\n";
	$s .= "exten => s, 2, Set(Q_E=0)\r\n";
	$s .= 'exten => s, 3, Set(Q_PROMPT_L_${Q_L}=${Q_PROMPT})'."\r\n";
	$s .= 'exten => s, 4, Set(Q_L=$[${Q_L}+1])'."\r\n";
	$s .= "exten => s, 5, Set(Q_PROMPT=prompt_".$row[0].")  ;; ".$row[1]."\r\n";
	$s .= "exten => s, 6, Set(Q_V=)\r\n";
	
	if ($row[2]==VOICEPROMPT_API) 
	{
		$read_var = "CHAN_Q_V";
		$read_max_digits = 10; // todo: use $row[6]
		$read_timeout = 10;
		$s .= "exten => s, n, Set(CHAN_Q_V=)\r\n";
	}

	$s .= "exten => s, n, Set(CHAN_PROMPT_ID=".$row[0].")\r\n";
	$s .= "exten => s, n, Set(CHAN_PROMPT_TS0=)\r\n";
	$s .= "exten => s, n, Read(".$read_var.",\"".$row[3]."\",".$read_max_digits.",,1,".$read_timeout.")\r\n";
	$s .= "exten => s, n, Set(CHAN_PROMPT_TS1=)\r\n";
	
	if ($row[2]==VOICEPROMPT_API)
	{
		// $s .= ""; // todo moh ==> beep every 10 seconds
		$s .= "exten => s, n, Set(CHAN_VX=".$row[8].")\r\n";
		$s .= "exten => s, n, Wait(60)\r\n";
		$s .= "exten => s, n(vxtimeout), Noop(API Response Timeout)\r\n";
		$s .= "exten => s, n, Set(CHAN_PROMPT_TS2=)\r\n";
		$s .= "exten => s, n, Goto(prompt__vx_timeout,s,1)\r\n";
		$s .= "exten => s, n, Hangup\r\n";
		$s .= "exten => s, n(vxreply), Noop(API Response OK)\r\n";
	}
	
	$s .= "exten => s, n, Set(CHAN_PROMPT_TS2=)\r\n";
	
	if ($row[2]==VOICEPROMPT_EXTEN)
	{
		$s .= "exten => s, n, Dial(PJSIP/".$row[5].")\r\n";
	}
	
	if ($row[2]==VOICEPROMPT_AGENTS)
	{
		$s .= 'exten => s, n, Set(MONITOR_FILENAME=/home/dat/recordings/${UNIQUEID})'."\r\n";
		$s .= 'exten => s, n, Queue(${CAMPAIGN_QUEUE_ID},,,,${CAMPAIGN_QUEUE_TIMEOUT})'."\r\n"; // both variables set on CHAN_WH
	}

	if ($row[2]==VOICEPROMPT_PLAYBACK || $row[2]==VOICEPROMPT_MENU || $row[2]==VOICEPROMPT_API)
	{
		$slast0 = "";
		$slast1 = "";
		$read_var_ = $read_var;
		if ($row[2]==VOICEPROMPT_API) $read_var_ = "CHAN_V_V";
		
		$q = "SELECT id, k, dst_id, dst_type FROM voicemap WHERE voiceprompt_id=?"; // nb order by pos
		$res2 = qryp ($q, "s", [$row[0]], 0, "db2"); 
		while ($row2 = mysqli_fetch_row ($res2))
		{
			if ($row2[3]==VOICEPROMPT_AGENTS) // check working hours for cid before routing to a usergroup/queue
			{
				$slast0 .= "exten => s, n, Set(CHAN_WH=)\r\n"; // re-eval working hours again
				$slast0 .= "exten => s, n, Wait(60)\r\n";
				$slast0 .= "exten => s, n, Hangup\r\n";
			}
	
			if (strlen($row2[1])<1) // dont eval gotoif -> goto next prompt (seq | default)
			{
				$slast1 .= 'exten => s, n, Goto(prompt_'.$row2[2].',s,1)'."\r\n";
				continue;
			}
			
			$s .= 'exten => s, n, GotoIf($["${'.$read_var_.'}"="'.$row2[1].'"]?prompt_'.$row2[2].',s,1)'."\r\n";
		}
		
		$s .= $slast0.$slast1;
		
		if ($row[2]==VOICEPROMPT_MENU)
		{
			$s .= 'exten => s, n, GotoIf($["${'.$read_var_.'}"=""]?prompt__blank,s,1)'."\r\n";
			$s .= 'exten => s, n, Goto(prompt__invalid,s,1)'."\r\n";
		}
	
		if ($row[2]==VOICEPROMPT_API)
		{
			$s .= "exten => s, n, Goto(prompt__vx_unk,s,1)\r\n";
		}
	}

	$s .= "exten => s, n, Hangup\r\n";

	fwrite ($fd, $s);
}

function dialplan_conf ($voiceprompt_id)
{
	$fdn = DAT."/conf/prompt_".$voiceprompt_id.".conf"; 
	$fd = fopen ($fdn, 'w'); 
	$q = "SELECT id, name, type, voicefile_ids, lvl, exten, dtmfmaxlen, recmaxlen, api FROM voiceprompt WHERE id=?";
	$row = qryp ($q, "s", [$voiceprompt_id], 1); 
	if ($row && $fd)
	{
		dialplan_prompt ($row, $fd);
	}
	fclose ($fd);
	rsync ();
	ami ("reload?");
	ami ("whr?");
} 

?>
