<?php

/*
update kase set final_status=status;
update kase set final_status=3 where status!=2 and escalated_to_id!=0;

update kase set assigned_to_id=created_by_id;
update kase set assigned_to_id=escalated_to_id WHERE escalated_to_id!=0;

update kase set escalated_by_id= ///5
*/

$FN = ["sendOTP"=>1, "verifyOTP"=>1, "resetAuth"=>1, "changeAuth"=>1, "dash"=>1, "wallonly"=>1, "agent"=>1, "chan"=>1, "sup"=>1, "msg"=>1, "msg_end"=>1]; // non-crud endpoints

$RESOURCES = array 
(
	"au"=>			array ("au","",			"1","0","0",	"Audit Trail", 		"","",			""), 
	"addr"=>		array ("addr","",		"1","0","0",	"Registered Address", 	"id DESC","",		""), 
	"otp"=>			array ("otp","",		"1","0","0",	"OTP", 			"","",			""), 
	"extens"=>		array ("exten","",		"1","0","0",	"WebRTC Extension", 	"","",			""), 
	"auth"=>		array ("auth","",		"0","0","0",	"Auth", 		"","",			""),
	"users"=>		array ("auth","user",		"3","0","0",	"User", 		"","",			""),
	"contacts"=>		array ("contact","",		"3","0","0",	"Contact", 		"fullname","",		""), 
	"profile"=>		array ("contact","profile",	"0","0","0",	"Profile", 		"","",			"contacts"), 

	"schedules"=>		array ("schedule","",		"3","0","0",	"Schedule", 		"id DESC","",		""), 
	"campaigns"=>		array ("campaign","",		"3","0","0",	"Campaign", 		"id DESC","",		""),	
	//"members"=>		array ("member","",		"3","0","0",	"Member", 		"","",			""), 		
	//"voiceprompts"=>	array ("voiceprompt","",	"3","0","0",	"VoicePrompt", 		"","",			""),	
	//"voicefiles"=>	array ("voicefile","",		"3","0","0",	"VoiceFile", 		"pos ASC","",		""),
	"categories"=>          array ("category","",           "3","0","0",    "Category",             "level,name","",	""), 
        "subcategories"=>       array ("category","subcategory","3","0","0",    "Category",             "level,name","",	"categories"), 

	"files"=>		array ("file","",		"1","0","0",	"File", 		"","",			""),
	"calls"=>		array ("chan","",		"0","0","0",	"Call", 		"","",			""), 
	"chanss"=>		array ("chan_ss","",		"0","0","0",	"Agent Session", 	"","",			""), 
        "pmessages"=>		array ("pmsg","",		"1","0","0",	"Message Session",	"id DESC","",		""), 
        "messages"=>		array ("msg","",		"1","0","0",	"Message", 		"id DESC","",		""), 

	"activities"=>		array ("activity","",		"3","0","0",	"Activity", 		"src_ts DESC","",	""), 
	"dispositions"=>	array ("disposition","dsp",	"3","0","0",	"Dispositions", 	"created_on DESC","",	""), 
	"actions"=>		array ("action","",		"1","0","0",	"Actions", 		"id DESC","",		""), 
	"attachments"=>		array ("attachment","",		"3","0","0",	"Attachment",		"","",			""), 			
	//"qas"=>			array ("qa","",			"1","0","0",	"Quality Assessment",	"","",			""), 
		
	"reporters"=>		array ("reporter","",		"3","0","0",	"Reporter", 		"","",			""), 
	"clients"=>		array ("client","",		"3","0","0",	"Client", 		"","",			""), 
	"perpetrators"=>	array ("perpetrator","",	"3","0","0",	"Perpetrator", 		"","",			""), 
	"services"=>		array ("service","",		"3","0","0",	"Services Offered", 	"","",			""), 
	"referals"=>		array ("referal","",		"3","0","0",	"Referals", 		"","",			""), 
	"client_referals"=>	array ("client_referal","",	"3","0","0",	"Client Referals",	"","",			""), 
	"cases"=>		array ("kase","case",		"3","0","0",	"Case", 		"","",			""), 
	"case_activities"=>	array ("kase_activity","ca",	"1","0","0",	"Case Activity", 	"","",			""), 
);

$RK=$RESOURCES;

// ===================================================================================

$RIGHTS_1 = array // sel:0,add:1,upd:2 // agent rights
(
	"au"=>		array ("1","0","0","0","0"),
	"addr"=>	array ("0","0","0","0","0"),
	"otp"=>		array ("0","0","0","0","0"),
	"auth"=>	array ("1","0","0","0","0","id=","auth_id"),
	"users"=>	array ("1","0","0","0","0"),
	"contacts"=>	array ("1","1","1","0","0"),
	"profile"=>	array ("1","0","1","0","0","id=","profile_id"), // 1177
	
	"schedules"=>	array ("1","0","0","0","0","user_id=","auth_id"),
	"campaigns"=>	array ("1","0","0","0","0"),
	"members"=>	array ("1","0","0","0","0"),
	"voicemaps"=>	array ("1","0","0","0","0"),
	"voiceprompts"=>array ("1","0","0","0","0"),
	"voicefiles"=>	array ("1","0","0","0","0"), 
	"categories"=>	array ("1","0","0","0","0"),
	"subcategories"=>array ("1","0","0","0","0"),

	"files"=>	array ("1","1","0","0","0"),		
	"calls"=>	array ("1","0","0","0","0","user_id=","auth_id"), 
	"chanss"=>	array ("1","0","0","0","0","user_id=","auth_id"),  
	"prompts"=>	array ("1","0","0","0","0"),
	"pmessages"=>	array ("1","1","0","0","0"),
	"messages"=>	array ("1","1","0","0","0"),
//	"emails"=>	array ("1","1","0","0","0"), 
			
	"activities"=>	array ("1","1","1","0","0","created_by_id=","auth_id"),	
	"dispositions"=>array ("1","1","1","0","0"),
	"actions"=>	array ("1","1","0","0","0"),
	"attachments"=>	array ("1","1","1","0","0"),
	"qas"=>		array ("1","1","0","0","0","chan_user_id=","auth_id"), 

	"reporters"=>	array ("1","1","1","0","0"),
	"clients"=>	array ("1","1","1","0","0"),
	"perpetrators"=>array ("1","1","1","0","0"),
	"services"=>	array ("1","1","1","0","0"),
	"referals"=>	array ("1","1","1","0","0"),
	"client_referals"=>	array ("1","1","1","0","0"),
	"cases"=>	array ("1","1","1","1","0","created_by_id=","auth_id"), // allow couselor to edit other peoples cases
	"case_activities"=>	array ("1","1","0","0","0"),
);

$RIGHTS_2 = array // sel:0,add:1,upd:2,overide-ctc-field:3 // supervisor rights
(
	"au"=>		array ("1","0","0","0","0"),
	"addr"=>	array ("0","0","0","0","0"),
	"otp"=>		array ("0","0","0","0","0"),
	"auth"=>	array ("1","0","0","0","0","id=","auth_id"),
	"users"=>	array ("1","0","0","0","0"),
	"contacts"=>	array ("1","1","1","0","0"),
	"profile"=>	array ("1","0","1","0","0","id=","profile_id"), // 1177

	"schedules"=>	array ("1","1","1","0","0"),
	"campaigns"=>	array ("1","0","0","0","0"),
	"members"=>	array ("1","0","0","0","0"),
	"voicemaps"=>	array ("1","0","0","0","0"),
	"voiceprompts"=>array ("1","0","0","0","0"),
	"voicefiles"=>	array ("1","0","0","0","0"), 
	"categories"=>	array ("1","0","0","0","0"),
	"subcategories"=>array ("1","0","0","0","0"),
	
	"files"=>	array ("1","1","0","0","0"),		
	"calls"=>	array ("1","0","0","0","0"), 
	"chanss"=>	array ("1","0","0","0","0","user_id=","auth_id"),  
	"prompts"=>	array ("1","0","0","0","0"),
	"pmessages"=>	array ("1","1","0","0","0"),
	"messages"=>	array ("1","1","0","0","0"),
//	"emails"=>	array ("1","1","0","0","0"), 
				
	"activities"=>	array ("1","1","1","0","0","created_by_id=","auth_id"),	
	"dispositions"=>array ("1","1","1","0","0"),
	"actions"=>	array ("1","1","0","0","0"),
	"attachments"=>	array ("1","1","1","0","0"),
	"qas"=>		array ("1","1","0","0","0"), 

	"reporters"=>	array ("1","1","1","0","0"),
	"clients"=>	array ("1","1","1","0","0"),
	"perpetrators"=>array ("1","1","1","0","0"),
	"services"=>	array ("1","1","1","0","0"),
	"referals"=>	array ("1","1","1","0","0"),
	"client_referals"=>	array ("1","1","1","0","0"),
	"cases"=>	array ("1","1","1","0","0"), // "created_by_id=","auth_id","created_by_role=1",""),
	"case_activities"=>	array ("1","1","0","0","0"),
);

$RIGHTS_3 = array // sel:0,add:1,upd:2 // casemanger rights
(
	"au"=>		array ("1","0","0","0","0"),
	"addr"=>	array ("0","0","0","0","0"),
	"otp"=>		array ("0","0","0","0","0"),
	"auth"=>	array ("1","0","0","0","0","id=","auth_id"),
	"users"=>	array ("1","0","0","0","0"),
	"contacts"=>	array ("1","1","1","0","0"),
	"profile"=>	array ("1","0","1","0","0","id=","profile_id"), // 1177
	
	"schedules"=>	array ("1","0","0","0","0"),
	"campaigns"=>	array ("1","0","0","0","0"),
	"members"=>	array ("1","0","0","0","0"),
	"voicemaps"=>	array ("1","0","0","0","0"),
	"voiceprompts"=>array ("1","0","0","0","0"),
	"voicefiles"=>	array ("1","0","0","0","0"), 
	"categories"=>	array ("1","0","0","0","0"),
	"subcategories"=>array ("1","0","0","0","0"),

	"files"=>	array ("1","1","0","0","0"),		
	"calls"=>	array ("1","0","0","0","0"), 
	"chanss"=>	array ("1","0","0","0","0","user_id=","auth_id"),  
	"prompts"=>	array ("1","0","0","0","0"),
	"pmessages"=>	array ("1","1","0","0","0"),
	"messages"=>	array ("1","1","0","0","0"),
//	"emails"=>	array ("1","1","0","0","0"), 
				
	"activities"=>	array ("1","1","1","0","0","created_by_id=","auth_id"),	
	"dispositions"=>array ("1","1","1","0","0"),
	"actions"=>	array ("1","1","0","0","0"),
	"attachments"=>	array ("1","1","1","0","0"),
	"qas"=>		array ("1","1","0","0","0"), 

	"reporters"=>	array ("1","1","1","0","0"),
	"clients"=>	array ("1","1","1","0","0"),
	"perpetrators"=>array ("1","1","1","0","0"),
	"services"=>	array ("1","1","1","0","0"),
	"referals"=>	array ("1","1","1","0","0"),
	"client_referals"=>	array ("1","1","1","0","0"),
	"cases"=>	array ("1","1","1","1","0","assigned_to_id=","auth_id","escalated_by_id=","auth_id"), // allow manager to edit other peoples cases
	"case_activities"=>	array ("1","1","0","0","0"),
);

$RIGHTS_4 = array // sel:0,add:1,upd:2 // case workerr
(
	"au"=>		array ("1","0","0","0","0"),
	"addr"=>	array ("0","0","0","0","0"),
	"otp"=>		array ("0","0","0","0","0"),
	"auth"=>	array ("1","0","0","0","0","id=","auth_id"),
	"users"=>	array ("1","0","0","0","0"),
	"contacts"=>	array ("1","1","1","0","0"),
	"profile"=>	array ("1","0","1","0","0","id=","profile_id"), // 1177

	"schedules"=>	array ("1","0","0","0","0","user_id=","auth_id"),	
	"campaigns"=>	array ("1","0","0","0","0"),
	"members"=>	array ("1","0","0","0","0"),
	"voicemaps"=>	array ("1","0","0","0","0"),
	"voiceprompts"=>array ("1","0","0","0","0"),
	"voicefiles"=>	array ("1","0","0","0","0"), 
	"categories"=>	array ("1","0","0","0","0"),
	"subcategories"=>array ("1","0","0","0","0"),

	"files"=>	array ("1","1","0","0","0"),		
	"calls"=>	array ("1","0","0","0","0","user_id=","auth_id"), 
	"chanss"=>	array ("1","0","0","0","0","user_id=","auth_id"),  
	"prompts"=>	array ("1","0","0","0","0"),
	"pmessages"=>	array ("1","1","0","0","0"),
	"messages"=>	array ("1","1","0","0","0"),
//	"emails"=>	array ("1","1","0","0","0"), 
			
	"activities"=>	array ("1","1","1","0","0","created_by_id=","auth_id"),	
	"dispositions"=>array ("1","1","1","0","0"),
	"actions"=>	array ("1","1","0","0","0"),
	"attachments"=>	array ("1","1","1","0","0"),
	"qas"=>		array ("1","1","0","0","0","chan_user_id=","auth_id"), 

	"reporters"=>	array ("1","1","1","0","0"),
	"clients"=>	array ("1","1","1","0","0"),
	"perpetrators"=>array ("1","1","1","0","0"),
	"services"=>	array ("1","1","1","0","0"),
	"referals"=>	array ("1","1","1","0","0"),
	"client_referals"=>	array ("1","1","1","0","0"),
	"cases"=>	array ("1","1","1","1","0","assigned_to_id=","auth_id"), // allow couselor to edit other peoples cases
	"case_activities"=>	array ("1","1","0","0","0"),
);

$RIGHTS_5 = $RIGHTS_4;

$RIGHTS_6 = $RIGHTS_1; // media account

$RIGHTS_99 = array // sel:0,add:1,upd:2,sel:id(other) // admin rights (same as supervisor+add/edit users)
(
	"au"=>		array ("1","0","0","0","0"),
	"addr"=>	array ("0","0","0","0","0"),
	"otp"=>		array ("0","0","0","0","0"),
	"extens"=>	array ("1","1","0","0","0"),
	"auth"=>	array ("1","0","0","0","0","id=","auth_id"),
	"users"=>	array ("1","1","1","0","0"),
	"contacts"=>	array ("1","1","1","0","0"),
	"profile"=>	array ("1","0","1","0","0","id=","profile_id"),  

	"schedules"=>	array ("1","1","1","0","0"),	
	"campaigns"=>	array ("1","1","1","0","0"),
	"members"=>	array ("1","1","1","0","0"),
	"voicemaps"=>	array ("1","1","1","0","0"),
	"voiceprompts"=>array ("1","1","1","0","0"),
	"voicefiles"=>	array ("1","1","1","0","0"), 
	"categories"=>	array ("1","1","1","0","0"),
	"subcategories"=>array ("1","1","1","0","0"),

	"files"=>	array ("1","1","0","0","0"),		
	"calls"=>	array ("1","0","0","0","0"), 
	"chanss"=>	array ("1","0","0","0","0","user_id=","auth_id"),  
	"prompts"=>	array ("1","0","0","0","0"),
	"pmessages"=>	array ("1","1","0","0","0"),
	"messages"=>	array ("1","1","0","0","0"),
//	"emails"=>	array ("1","1","0","0","0"), 
				
	"activities"=>	array ("1","1","1","0","0","created_by_id=","auth_id"),	
	"dispositions"=>array ("1","1","1","0","0"),
	"actions"=>	array ("1","1","0","0","0"),
	"attachments"=>	array ("1","1","1","0","0"),
	"qas"=>		array ("1","1","0","0","0"), 
	
	"reporters"=>	array ("1","1","1","0","0"),
	"clients"=>	array ("1","1","1","0","0"),
	"perpetrators"=>array ("1","1","1","0","0"),
	"services"=>	array ("1","1","1","0","0"),
	"referals"=>	array ("1","1","1","0","0"),
	"client_referals"=>	array ("1","1","1","0","0"),
	"cases"=>	array ("1","1","1","0","0"), // "created_by_id=","auth_id","created_by_role=1",""),
	"case_activities"=>	array ("1","1","0","0","0"),
);

// ===================================================================================

$METRICS = array 
(
	"case_count"=>array ("COUNT(DISTINCT kase.id)",		"","","",  "","",  ""),

	"kase_count"=>array ("COUNT(DISTINCT kase.id)",		"","","",  "","",  ""),

	"client_count"=>array ("COUNT(DISTINCT client.id)",		"","","",  "","",  ""),

	"perpetrator_count"=>array ("COUNT(DISTINCT perpetrator.id)",		"","","",  "","",  ""),

	"service_count"=>array ("COUNT(DISTINCT service.id)",		"","","",  "","",  ""),

	"referal_count"=>array ("COUNT(DISTINCT referal.id)",		"","","",  "","",  ""),

	"call_count"=>array ("COUNT(DISTINCT chan.id)",		"","","",  "","",  ""),

	"chan_count"=>array ("COUNT(DISTINCT chan.id)",		"","","",  "","",  ""),

	"pmessage_count"=>array ("COUNT(DISTINCT pmsg.id)",		"","","",  "","",  ""),
	
	"pmsg_count"=>array ("COUNT(DISTINCT pmsg.id)",		"","","",  "","",  ""),
	
	"disposition_count"=>array ("COUNT(DISTINCT disposition.id)",		"","","",  "","",  ""),
		
	"in_count"=>array ("COUNT(id)",				"","","",  "","",  ""),

	"unique_count"=>array ("COUNT(is_repeat)",		"phone","IF(COUNT(phone)>1,1,0) is_repeat","COUNT(phone)",  "is_repeat",":0::isrepeat:1",  ""),
	"in_attempts"=>array ("SUM(n)/COUNT(n)",		"phone","COUNT(phone) n","COUNT(phone)/COUNT(DISTINCT phone)",  "","",  ""),

	"fcr"=>array ("COUNT(DISTINCT phone)",			"","","",  "","",  "hangup_status=5 "), 

	"sla_count"=>array ("COUNT(id)",			"","","",  "","",  "hangup_status IN (4,5) "),

	"wait_sum"=>array ("SUM(wait_time_tot)",		"","","",  "","",  "hangup_status IN (4,5) "),
	"wait_max"=>array ("MAX(wait_time_tot)",		"","","",  "","",  ""),
	"wait_min"=>array ("MIN(wait_time_tot)",		"","","",  "","",  ""),

	"talk_sum"=>array ("SUM(talk_time)",			"","","",  "","", "hangup_status=5 "),
	"talk_max"=>array ("MAX(talk_time)",			"","","",  "","", ""),
	"talk_min"=>array ("MIN(talk_time)",			"","","",  "","", ""),
	
	"hold_sum"=>array ("SUM(hold_time)",			"","","",  "","",  "hangup_status=5 && hold_time!=0 "),
	"hold_max"=>array ("MAX(hold_time)",			"","","",  "","",  ""),
	"hold_min"=>array ("MIN(hold_time)",			"","","",  "","",  ""),
	
	"usage_sum"=>array ("SUM(trunk_usage)",			"","","",  "","",  ""),
	"usage_max"=>array ("MAX(trunk_usage)",			"","","",  "","",  ""),
	"usage_min"=>array ("MIN(trunk_usage)",			"","","",  "","",  ""),

	"billing"=>array ("SUM(IF(vector=2,talk_time*call_rate,0))",		"","","",  "","",  "hangup_status=5 "),
	
	"in_available"=>array ("SUM(in_available)",				"","","",  "","",  ""),
	"in_occupied"=>array ("SUM(in_occupied)",				"","","",  "","",  ""),
	"in_availability"=>array ("(SUM(in_available)*100)/SUM(duration)",	"","","",  "","",  ""),
	"in_occupancy"=>array ("(SUM(in_occupied)*100)/SUM(duration)",		"","","",  "","",  ""),

	"out_available"=>array ("SUM(out_available)",				"","","",  "","",  ""),
	"out_occupied"=>array ("SUM(out_occupied)",				"","","",  "","",  ""),
	"out_availability"=>array ("(SUM(out_available)*100)/SUM(duration)",	"","","",  "","",  ""),
	"out_occupancy"=>array ("(SUM(out_occupied)*100)/SUM(duration)",	"","","",  "","",  ""),
	
	"shift_duration"=>array ("SUM(duration)",		"","","",  "","",  ""),

	"score"=>array ("SUM(score)",				"","","",  "","",  ""),
);


// ===================================================================================

$au_def = array 
(
	array ("id","",			"0","2","","",	"","","", 	"",""),
	array ("created_on","",		"0","3","","",	"","","", 	"",""),
	array ("created_by","",		"0","2","","",	"","","", 	"",""),
	array ("created_by_id","",	"0","2","","",	"","","", 	"",""),

	array ("aub_id","",		"1","2","","",	"","","", 	"",""), 
	array ("row_id","",		"1","2","","",	"","","", 	"",""), 
	array ("t","",			"1","2","","",	"","","", 	"",""), 
	array ("k","",			"1","2","","",	"","","", 	"",""), 
	array ("v","",			"1","1","","",	"","","", 	"",""), 
	array ("v_","",			"1","1","","",	"","","", 	"",""), 

);

$addr_def = array 
(
	array ("id","",				"0","2","","",	"","","", 	"",""),
	array ("created_on","",			"0","3","","",	"","","", 	"",""),
	array ("created_by","",			"0","2","","",	"","","", 	"",""),
	array ("created_by_id","",		"0","2","","",	"","","", 	"",""),

	array ("addr","",			"1","2","u","",	"","","", 	"",""), 
	array ("type","",			"1","2","","",	"","","", 	"",""), 

	array ("auth_id","",			"1","2","u","",	"","","", 	"",""), 
	array ("contact_id","",			"1","2","u","",	"","","", 	"",""), 
	array ("contact_fullname","",		"1","2","","",	"","","", 	"",""), 

);

$otp_def = array 
(
	array ("id","",				"0","2","","",	"","","", 	"",""),
	array ("created_on","",			"0","3","","",	"","","", 	"",""),
	array ("created_by","",			"0","2","","",	"","","", 	"",""),
	array ("created_by_id","",		"0","2","","",	"","","", 	"",""),

	array ("otp","",			"1","2","","",		"","","", 	"",""), 
	array ("expiry","",			"1","3","","",		"","","", 	"",""), 
	array ("action","",			"1","2","","",		"","","", 	"",""), 

	array ("addr_id","",			"1","2","m","f", 	"","","", 	"",""), 
	array ("addr_addr","",			"1","2","m","",		"","","", 	"",""), // /[1-9][0-9]{9,12}/
	array ("addr_type","",			"1","2","","",		"","","", 	"",""), 

	array ("auth_id","",			"1","2","m","f",	"","","", 	"",""), // 'm' flag means users cannot selfregister / if self-register will be null forn new
	array ("contact_id","",			"1","2","","", 		"","","", 	"",""), 
	array ("contact_fullname","",		"1","2","","",	"","","", 	"",""), 
);

$extens_def = array 
(
	array ("id","",				"0","2","","",	"","","", 	"",""),
	array ("created_on","",			"0","3","","",	"","","", 	"",""),
	array ("created_by","",			"0","2","","",	"","","", 	"",""),
	array ("created_by_id","",		"0","2","","",	"","","", 	"",""),
	array ("user_id","",			"1","2","","",	"","","", 	"",""), 
);

$auth_def = array 
(
	array ("id","",				"0","2","","", "","","", "ID",""),
	array ("created_on","",			"0","3","","", "","","", "Created On",""),
	array ("created_by","",			"0","2","","", "","","", "Created By",""),
	array ("created_by_id","",		"0","2","","", "","","", "Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", "Created By Role",""),

	array ("usn","",			"3","2","u","", "","","", "Username",""),
	array ("role","",			"3","2","m","", "","","", "Role",""),
	array ("exten","",			"4","2","","", "extens","id","", "WebTRC Extension",""), // auto generated
	array ("mac","",			"1","2","","", "","","", "Phone MAC Address",""), // for dhcp autoprovisioning
        array ("is_active","",                  "3","2","v","", "","1","", "Active",""),

	array ("contact_id","contact_id",	"1","2","","f", "","","", "Contact ID",""),
	array ("contact_fullname","",		"4","2","","", "contacts","fullname","", "Fullname",""),
	array ("contact_fname","",		"4","2","m","", "contacts","fname","", "First Name",""),
	array ("contact_lname","",		"4","2","","", "contacts","lname","", "Last Name",""),
	array ("contact_phone","",		"4","2","","p", "contacts","phone","", "Phone",""),
	array ("contact_email","",		"4","2","","", "contacts","email","", "Email",""),
	array ("contact_location","",		"4","2","","", "contacts","location","", "Location",""),
	
	array ("last_break","",			"0","2","","", "","","", "Last Break ",""),
	array ("last_break_ts","",		"0","2","","", "","","", "Last Break Time",""),
	array ("available","",			"0","2","","", "","","", "Available Duration",""),
);
$users_def = $auth_def;

$contacts_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
	
	array ("fullname","",			"4","1","","", "contacts","CONCAT(TRIM(fname),' ',TRIM(lname))","",	"Fullname",""),
	array ("fname","",			"3","1","m","", "","","",	"Name",""),
	array ("lname","",			"3","1","","",  "","","",	"Last Name",""),

	array ("phone","",			"3","1","","p", "","","",	"Phone",""), // todo: regex
	array ("email","",			"3","2","","", "","","",	"Email",""),
	array ("phone2","",			"3","2","","p", "","","",	"Alternative Contact",""), // todo: remove this --> create new contact (same details) linked to primary

	array ("dob","",			"3","2","","", "","","",	"Date of Birth",""),
	array ("age","",			"3","2","","", "","","",	"Age",""),
	array ("age_group_id","",		"3","2","","f", "","","",	"Age Group ID",""),
	array ("age_group","",			"3","2","","", "","","",	"Age Group",""),
	array ("sex_id","",			"3","2","","f", "","","",	"Gender ID",""),
	array ("sex","",			"3","2","","", "","","",	"Gender",""),

	array ("national_id_type_id","",	"3","2","","", "","","",	"ID Type ID",""),
	array ("national_id_type","",		"3","2","","", "","","",	"ID Type",""),
	array ("national_id","",		"3","2","","", "","","",	"National ID",""),
	array ("address","",			"3","1","","", "","","",	"Address",""),
	array ("residence","",			"3","2","","", "","","",	"Residence",""),

	array ("location_id","",		"3","2","","f", "","","",	"Location ID","",    "category","level","location_id_"),
	array ("location","",			"3","2","","", "","","",	"Location",""),
	array ("nationality_id","",		"3","2","","f", "","","",	"Nationality ID",""),
	array ("nationality","",		"3","2","","", "","","",	"Nationality",""),
	array ("tribe_id","",			"3","2","","f", "","","",	"Tribe ID",""),
	array ("tribe","",			"3","2","","", "","","",	"Tribe",""),
	array ("lang_id","",			"3","2","","f", "","","",	"Language ID",""),
	array ("lang","",			"3","2","","", "","","",	"Language",""),
	
	array ("landmark","",			"3","1","","", "","","",	"Nearest Landmark",""),

	array ("location_id_0","",		"3","2","","", "","","",	"",""),
	array ("location_id_1","",		"3","2","","", "","","",	"",""),
	array ("location_id_2","",		"3","2","","", "","","",	"",""),
	array ("location_id_3","",		"3","2","","", "","","",	"",""),
	array ("location_id_4","",		"3","2","","", "","","",	"",""),
	array ("location_id_5","",		"3","2","","", "","","",	"",""),
	array ("location_id_6","",		"3","2","","", "","","",	"",""),
	
	array ("location_0","",			"3","2","","", "","","",	"",""),
	array ("location_1","",			"3","2","","", "","","",	"",""),
	array ("location_2","",			"3","2","","", "","","",	"",""),
	array ("location_3","",			"3","2","","", "","","",	"",""),
	array ("location_4","",			"3","2","","", "","","",	"",""),
	array ("location_5","",			"3","2","","", "","","",	"",""),
	array ("location_6","",			"3","2","","", "","","",	"",""),
	
	array ("reporter_count","",		"0","4","","", "","","", 	"Is Reporter",""),
	array ("perp_count","",			"0","4","","", "","","", 	"Is Perpetrator",""),
	array ("client_count","",		"0","4","","", "","","", 	"Is Client",""),
	array ("is_refugee","",			"3","2","","", "","","",	"Contact Is Refugee","::yesno:0:2"),

	// applied only on select reporter (auto creates a copy of contact with new phone number) // avoid overriting the phone number
	// array ("ref_contact_id","",		"1","2","h","", "","","",	"Ref Contact ID",""),
	// array ("primary_contact_id","",	"1","2","h","", "","","",	"Primary Contact ID",""), 

);
$profile_def = $contacts_def;

// ----------------------------

$campaigns_def = array 
(
	array ("id","",				"0","2","","", "","","", "ID",""),
	array ("created_on","",			"0","3","","", "","","", "Created On",""),
	array ("created_by","",			"0","2","","", "","","", "Created By",""),
	array ("created_by_id","",		"0","2","","", "","","", "Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", "Created By Role",""),

	array ("name","",			"3","2","u","", "","","", 	"Name",""),
	array ("callerid","",			"3","2","m","",	"","","", 	"CallerID",""),
	array ("campaign","",			"1","2","m","", "","","",	"Type",""),

	array ("voiceprompt_id","voiceprompt_id","3","2","m","f", "","","", 	"IVR",""), // if queue -> fallback to queue voice menu acts as preprocessor
	array ("voiceprompt_name","",		"3","2","","", "","","", 	"IVR Name",""), // destination
	array ("voiceprompt_type","",		"3","2","","", "","","", 	"IVR Type",""), // destination

	array ("category_id","",		"3","2","m","f", "","","",	"Disposition List",""),
	array ("category_name","",		"3","1","","", "","","", 	"Category Name",""),
	array ("category_fullname","",		"3","1","","", "","","", 	"Category Full Name",""),

	array ("member_count","",		"4","4","","", 	"members","COUNT(id)","", 	"Member Count",""),
	array ("members","",			"4","1","","", 	"members","GROUP_CONCAT(user_usn ORDER BY user_usn)","", 	"Members",""),

	array ("agent_ring_strategy","",	"3","2","","", "","","",	"Agent Ring Strategy",""), // ringall, roundrobin, did-first
	array ("agent_ring_timeout","",		"3","4","","", 	"","","", 	"Agent Ring Timeout",""),
	array ("agent_wrapup","",		"3","4","","", 	"","","", 	"Agent Wrapup",""), 
	array ("wait_sla_target","",		"3","4","","", 	"","","", 	"SLA Target",""),
	array ("hold_sla_target","",		"3","4","","", 	"","","", 	"SLA Target",""),
	array ("queue_timeout","",		"3","4","","", 	"","","", 	"Queue Timeout",""),

	array ("moh_ids","",			"4","2","","",	"moh","GROUP_CONCAT(file_id ORDER BY id)","", 	"Voice File IDs",""),
	array ("moh_names","",			"4","1","","",	"moh","GROUP_CONCAT(file_name ORDER BY pos)","", "Voice File",""),
	array ("moh_duration","",		"4","5","","", 	"moh","SUM(file_duration)","", 	"Voice Duration",""),

	array ("exit_id","",			"3","2","","f", "","","", 	"Exit ID",""),
	array ("exit_name","",			"3","1","","",   "","","", 	"Exit",""),
	array ("exit_type","",			"3","2","","",   "","","", 	"Exit Type",""),

	array ("ring_timeout","",		"3","4","","", 	"","","", 	"Ring Timeout",""),
	array ("reattempts","",			"3","4","","", 	"","","", 	"Reattempts",""),
	array ("reattempt_interval","",		"3","4","","", 	"","","", 	"Reattempt Duration",""),

	array ("lead_count","",			"4","4","","",   "leads","COUNT(id)","", 	"Lead Count",""),
	
	array ("answered","",				"0","4","","", "","","", "Answered",""), 
	array ("resched","",				"0","4","","", "","","", "Rescheduled",""), 
	array ("unreachable","",			"0","4","","", "","","", "Unreachable",""),
	array ("progress","",				"0","4","","", "","","", "Progress",""),
	array ("avg_talk","",				"0","4","","", "","","", "Avg Talk Time",""), 
	array ("avg_hold","",				"0","4","","", "","","", "Avg Hold Time",""),
	array ("max_talk","",				"0","4","","", "","","", "Max Talk Time",""), 
	array ("max_hold","",				"0","4","","", "","","", "Max Hold Time",""),
	array ("not_dialed","",				"0","4","","", "","","", "Not Dialed",""),
	
	array ("ans_count","",				"0","4","","", "","","", "Answered",""),
	array ("ab_count","",				"0","4","","", "","","", "Abandoned",""),
	array ("ivr_count","",				"0","4","","", "","","", "IVR",""),
	array ("sla_wait","",				"0","4","","", "","","", "SLA",""),
	array ("ans_avg_talk_time","",			"0","4","","", "","","", "Avg Talk",""),
	array ("hold_avg","",				"0","4","","", "","","", "Avg Hold",""),
	
	array ("occupied","",			"0","2","","",   "","","",   "Occupied",""),  
        array ("occupancy","",			"0","2","","",   "","","",   "Occupancy",""),  
        array ("available","",			"0","2","","",   "","","",   "Available",""),  
        array ("availability","",		"0","2","","",   "","","",   "Availability",""),  
	array ("agents_online","",		"0","2","","",   "","","",   "Agents Online",""),  

);

$schedules_def = array 
(
	array ("id","",				"0","2","","", "","","", "ID",""),
	array ("created_on","",			"0","3","","", "","","", "Created On",""),
	array ("created_by","",			"0","2","","", "","","", "Created By",""),
	array ("created_by_id","",		"0","2","","", "","","", "Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", "Created By Role",""),

	array ("daterange","",			"3","2","m","D", "","","",	"Date Range",""),
	array ("dayofweek","",			"3","2","","W", "","","",	"Day of Week",""), 
	array ("timerange","",			"3","2","","T", "","","",	"Date Range",""),
	array ("dt0","",			"3","2","","", "","","",	"dt0",""),
	array ("dt1","",			"3","2","","", "","","",	"dt1",""),
	array ("dayofweek_mask","",		"3","2","","", "","","",	"Day of Week Mask",""), 
	array ("tm0","",			"3","2","","", "","","", 	"Start",""),
	array ("tm1","",			"3","2","","", "","","", 	"End",""), 

	array ("priority","",			"3","2","m","", "","","", 	"Action",""), // inactive, wh, ooo, reattempt
	array ("resource","",			"3","2","m","", "","","", 	"Schedule Type",""), // campaign, user, callback
	
	array ("campaign_id","",		"3","2","","f", "","","",	"Campaign ID",""), 
	array ("campaign_name","",		"3","2","","", "","","",	"Campaign Name",""), 
	array ("campaign_callerid","",		"3","2","","", "","","",	"Campaign Caller ID",""), 
	array ("campaign_campaign","",		"3","2","","", "","","",	"Campaign Type",""), 
		
	array ("voiceprompt_id","",		"3","2","","f", "","","", 	"IVR ID",""),  // root only
	array ("voiceprompt_name","",		"3","2","","", "","","", 	"IVR Name",""), 
	array ("voiceprompt_type","",		"3","2","","", "","","", 	"IVR Type",""), 
	
	array ("user_id","",			"3","2","","f", "","","",	"User ID",""), 
	array ("user_usn","",			"3","2","","", "","","",	"User Name",""), 
	array ("user_role","",			"3","2","","", "","","",	"User Role",""), 
	array ("user_exten","",			"3","2","","", "","","",	"User Exten",""), 
);

$members_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("user_id","",			"1","2","m","f", "","","", 	"Auth ID",""),
	array ("user_usn","",			"1","2","","", "","","", 	"Username",""), // same as otp handle
	array ("user_role","",			"1","2","","", "","","", 	"Role",""),
	array ("user_exten","",			"1","2","","", "","","", 	"Extension",""),

	array ("contact_id","",			"1","2","m","f", "","","", 	"Contact ID",""),
	array ("contact_fullname","",		"1","2","","", "","","", 	"First Name",""),
	array ("contact_fname","",		"1","2","","", "","","", 	"Last Name",""),
	array ("contact_lname","",		"1","2","","", "","","", 	"Fullname",""),
	array ("contact_phone","",		"1","2","","", "","","", 	"Phone",""),
	array ("contact_email","",		"1","2","","", "","","", 	"Email",""),	

	array ("campaign_id","",		"3","2","m","", "","","", 	"Campaign ID",""),
	// array ("campaign_name","",		"1","2","","", "","","", "Campaign Name",""),
	// array ("campaign_campaign","",		"1","2","","", "","","", "Campaign Type",""),
	// array ("campaign_campaign","",		"1","2","","", "","","", "Campaign Type",""),
	// array ("campaign_campaign","",		"1","2","","", "","","", "Campaign Type",""),
);

$categories_def = array 
(
	array ("id","",				"0","2","","", "","","", "ID",""),
	array ("created_on","",			"0","3","","", "","","", "Created On",""),
	array ("created_by","",			"0","2","","", "","","", "Created By",""),
	array ("created_by_id","",		"0","2","","", "","","", "Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", "Created By Role",""),

	array ("name","",			"3","1","u","", "","","",	"Category Name",""),
	array ("fullname","",			"4","1","","", "subcategories","CONCAT(category_fullname, '^', name)","", 		"Fullname",""),
	array ("fullname_id","",		"4","1","","", "subcategories","CONCAT(category_fullname_id, id, ':', name, '^')","", 	"Fullname ID",""),

	array ("category_id","",		"1","6","","", "","","",	"Parent ID",""),
	array ("category_name","",		"3","1","","", "","","", 	"Parent Name",""),
	array ("category_fullname","",		"3","1","","", "","","", 	"Parent Full Name",""),
	array ("category_fullname_id","",	"3","1","","", "","","", 	"Parent Full Name ID",""),
	array ("category_level","",		"3","1","","", "","","", 	"Parent Level",""),
	array ("category_category_id","",	"3","1","","", "","","", 	"Parent Category ID",""),
	array ("category_root_id","",		"3","1","","", "","","", 	"Root ID",""),
	array ("category_root_name","",		"3","1","","", "","","", 	"Root Name",""),

	array ("level","",			"4","2","","", "subcategories","category_level+1","", "Level",""),
	array ("root_id","",			"4","2","","", "subcategories","IF(category_category_id=0,category_id,category_root_id)","", 	"Root ID",""),
	array ("root_name","",			"4","2","","", "subcategories","IF(category_category_id=0,category_name,category_root_name)","", "Root Name",""),
	
	array ("uuid","",			"3","1","","", "","","",	"UUID",""),
	array ("code","",			"3","1","","", "","","",	"Code",""),

	array ("isactive","",			"3","1","v","", "","1","",	"Active",""),
	array ("category_id_","",		"5","2","","", "subcategories","IF(isactive='1',category_id,'-9')","",	"Link ID",""),
	array ("root_id_","",			"5","2","","", "subcategories","IF(isactive='1',root_id,'-9')","",	"Root Link ID",""),
);
$subcategories_def = $categories_def; //  

// ------------------------------

$files_def = array   
(
	array ("id","",				"1","2","","", "","","",	"ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On",""),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","f", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("name","",			"1","1","","", "","","",	"",""), 
	array ("mime","",			"1","1","","", "","","",	"",""),
	array ("size","",			"1","5","","", "","","",	"",""),
	array ("uploadstatus","",		"1","2","","", "","","",	"",""),
	array ("movestatus","",			"1","2","","", "","","",	"",""),

	array ("channels","",			"1","2","","", "","","",	"",""),
	array ("sample_rate","",		"1","2","","", "","","",	"",""),
	array ("duration","",			"1","2","","", "","","",	"",""),

	array ("batch_id","",			"1","2","","", "","","",	"",""),
);

$dispositions_agg_clause = 'GROUP_CONCAT(DISTINCT CONCAT(
if(disposition_id>0,disposition,""), 
if(case_id>0,CONCAT(" - ",case_id),"") 
) SEPARATOR "; ")';

$contacts_agg_clause = 'GROUP_CONCAT(DISTINCT CONCAT(
if(reporter_id>0,reporter_fullname,""), 
if(reporter_sex_id>0,CONCAT(", ",REPLACE(reporter_sex,"^","")),""),  
if(reporter_age_group_id>0,CONCAT(", ",REPLACE(reporter_age_group,"^","")),""), 
if(reporter_location_id>0,CONCAT(", ",reporter_location),"") 
) SEPARATOR "; ")';

$calls_def = array // SELECT phone, hangup_reason, hangup_status
(
	array ("uniqueid","",			"0","2","","",   "","","",   "ID",""), 
        array ("chan_ts","",			"0","3","","",   "","","",   "Date","d M Y H:i:s"),
        array ("context","",			"0","2","","",   "","","",   "",""),
        array ("trunk","",			"0","2","","",   "","","",   "Trunk DID",""),
        array ("phone","",			"0","1","","",   "","","",   "Phone",""),  
        array ("usr","",			"0","2","","",   "","","",   "Extension",""), 
        array ("usr_name","",			"0","2","","",   "","","",   "Extension CID Name",""), 
        array ("ring_time","",			"0","4","","",   "","","",   "",""),  
        array ("wait_time","",			"0","4","","",   "","","",   "",""),  
        array ("queue_time","",			"0","4","","",   "","","",   "",""),  
        array ("wait_time_tot","",		"0","4","","",   "","","",   "Wait Time",""),  
        array ("talk_time","",			"0","4","","",   "","","",   "Talk Time",""),  
        array ("hold_time","",			"0","2","","",   "","","",   "Hold Time",""),  
        array ("hangup_reason","",		"0","2","","",   "","","",   "Hangup By",""),  
        array ("hangup_status","",		"0","2","","",   "","","",   "Hangup Status",""),  
	array ("hangup_status_txt","",		"0","2","","",   "","","",   "Hangup Status","::hangup_status:0:1"),  
        array ("sla_band_queue","",		"0","2","","",   "","","",   "SLA Queue","::sla:0:1:"), 
        array ("sla_band_hold","",		"0","2","","",   "","","",   "SLA Hold","::sla:0:1:"), 
	array ("sla_target_queue","",		"0","2","","",   "","","",   "",""), 
        array ("yr","",				"0","2","","",   "","","",   "Year",":d:y:0: "), 
        array ("mn","",				"0","2","","",   "","","",   "Month",":d:my:0: "), 
        array ("wk","",				"0","2","","",   "","","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"0","2","","",   "","","",   "Date",":d:dmy:0: "), 
        array ("dth","",			"0","2","","",   "","","",   "Date Hour",":d:dmyh:0: "), 
 	array ("h","",				"0","2","","",   "","","",   "Hour",":h:h:0:"), 
        array ("vector","",			"0","2","","",   "","","",   "Direction","::vector:0:1:"),  

	array ("user_id","",			"0","2","","",   "","","",   "User ID",""),
	array ("user_name","",			"0","2","","",   "","","",   "User Name",""),
	array ("user_role","",			"0","2","","",   "","","",   "User Role",""),
	
	array ("qa_done","",			"4","2","","",   "qas","IF(id>0,1,0)","",  	"QA Done",""), 
	array ("qa_id","",			"4","2","","",   "qas","id","",   		"QA ID",""), 
	array ("qa_score","",			"4","2","","",   "qas","total_score_p","",   	"QA Score",""), 

        array ("dispositions","",		"4","1","","",  "dispositions", $dispositions_agg_clause,"",		"Dispositions",""),  
	array ("contacts","",			"4","1","","",  "dispositions", $contacts_agg_clause,"",		"Contacts",""),  
        array ("has_case_id","",		"4","2","","",  "dispositions", "IF(SUM(IF(case_id>0,1,0))>0,1,0)","",  "Has Case ID",""),
        
);

$chanss_def = array
(
	array ("uniqueid","",			"0","2","","",   "","","",   "ID",""), 
        array ("chan_ts","",			"0","3","","",   "","","",   "Date","d M Y H:m"),  
        array ("usr","",			"0","2","","",   "","","",   "Extension",""), 

        array ("state_hangup","",		"0","2","","",   "","","",   "End Time",""),  
	array ("last_call","",			"0","2","","",   "","","",   "Last Call",""),  
        array ("occupied","",			"0","2","","",   "","","",   "Occupied",""),  
        array ("occupancy","",			"0","2","","",   "","","",   "Occupancy",""),  
        array ("available","",			"0","2","","",   "","","",   "Available",""),  
        array ("availability","",		"0","2","","",   "","","",   "Availability",""),  
        
        array ("yr","",				"0","2","","",   "","","",   "Year",":d:y:0: "),      
        array ("mn","",				"0","2","","",   "","","",   "Month",":d:my:0: "), 
        array ("wk","",				"0","2","","",   "","","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"0","2","","",   "","","",   "Date",":d:dmy:0: "), 
        array ("hr","",				"0","2","","",   "","","",   "DateHour",":d:dmyh:0: "), 
	array ("hour","",			"0","2","","",   "","","",   "Hour",""), 
);

$pmessages_def = array
(
        array ("id","",                         "0","2","","", "","","",        "",""),
        array ("created_on","",                 "0","3","","", "","","",        "",""),
        array ("created_by","",                 "0","2","","", "","","",        "",""),
        array ("created_by_id","",              "0","2","","", "","","",        "",""),
        array ("created_by_role","",            "0","2","","", "","","",        "Created By Role",""),
  
        array ("src","",                        "1","2","m","", "","","",       "Channel",""),
        array ("src_ts","",                     "1","3","","",  "","","",       "Channel Timestamp",""), 
        array ("src_uid","",                    "1","2","m","", "","","",       "Channel Uniqueid",""), // msgid
        array ("src_uid2","",                   "1","2","","",  "","","",       "Activity Uniqueid",""),// activity_id
        array ("src_address","",                "1","2","","",  "","","",       "Channel Address",""),
        array ("src_usr","",                    "1","2","","",  "","","",       "Channel User",""),
        array ("src_vector","",                 "1","2","m","", "","","",       "Channel Direction",""),
        array ("src_callid","",                 "1","2","m","","","","",        "Channel Call ID",""),  // sessionid
        array ("src_campaign_id","",            "1","2","","",  "","","",       "Channel Campaign ID",""),
        array ("src_action_id","",              "1","2","","",  "","","",       "Channel Action ID",""),
        array ("src_status","",                 "1","2","","",  "","","",       "Channel Status",""),
	array ("src_mime","",			"1","2","","",  "","","",       "Message mime",""),

        array ("in_count","",                   "4","4","","",  "messages","SUM(IF(src_vector=1,1,0))","",      "Received Count",""),
        array ("out_count","",                  "4","4","","",  "messages","SUM(IF(src_vector=2,1,0))","",      "Sent Count",""),
        array ("last_msg_id","",                "4","2","","",  "messages","MAX(id)","last_msg_id",             "Last Message ID",""),
        array ("last_msg_vector","",            "5","2","","",  "messages","src_vector","",                     "Last Message Direction",""),
        array ("src_msg","",			"5","2","m","", "messages","src_msg","",                        "Last Message",""),
        
        array ("yr","",				"4","2","","",   "pmessages","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(src_ts)),'-01-01'))","",   "Year",":d:y:0: "), 
        array ("mn","",				"4","2","","",   "pmessages","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(src_ts)),'-',MONTH(FROM_UNIXTIME(src_ts)),'-01'))","",   "Month",":d:my:0: "), 
        array ("wk","",				"4","2","","",   "pmessages","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts))) - (DAYOFWEEK(FROM_UNIXTIME(src_ts))*86400)","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"4","2","","",   "pmessages","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts)))","",   "Date",":d:dmy:0: "), 
	array ("dth","",			"4","2","","",   "pmessages","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts))) + (HOUR(FROM_UNIXTIME(src_ts))*3600)","",   "Hour",":d:dmyh:0: "), 
        array ("h","",				"4","2","","",   "pmessages","HOUR(FROM_UNIXTIME(src_ts))","",   	"Hour",""), 
        
	array ("dispositions","",		"4","1","","",  "dispositions", $dispositions_agg_clause,"",		"Dispositions",""),  
	array ("contacts","",			"4","1","","",  "dispositions", $contacts_agg_clause,"",		"Contacts",""),  

);      

$messages_def = array
(
        array ("id","",                         "0","2","","", "","","",        "",""),
        array ("created_on","",                 "0","3","","", "","","",        "",""),
        array ("created_by","",                 "0","2","","", "","","",        "",""),
        array ("created_by_id","",              "0","2","","", "","","",        "",""),
        array ("created_by_role","",            "0","2","","", "","","",        "Created By Role",""),

        array ("src","",                        "1","2","m","", "","","",       "Channel",""),
        array ("src_ts","",                     "1","2","","",  "","","",       "Channel Timestamp",""),
        array ("src_uid","",                    "1","2","m","", "","","",       "Channel Uniqueid",""), // msgid
        array ("src_uid2","",                   "1","2","","",  "","","",       "Activity Uniqueid",""),// activity_id
        array ("src_address","",                "1","2","","",  "","","",       "Channel Address",""),
        array ("src_usr","",                    "1","2","","",  "","","",       "Channel User",""),
        array ("src_vector","",                 "1","2","m","", "","","",       "Channel Direction",""),
        array ("src_callid","",                 "1","2","m","","","","",        "Channel Call ID",""),  // sessionid
        array ("src_campaign_id","",            "1","2","","",  "","","",       "Channel Campaign ID",""),
        array ("src_action_id","",              "1","2","","",  "","","",       "Channel Action ID",""),
        array ("src_status","",                 "1","2","","",  "","","",       "Channel Status",""),
       	array ("src_mime","",			"1","2","","",  "","","",       "Message mime",""),
        array ("src_msg","",			"1","2","m","", "","","",       "Message",""),
);


// ------------------------------

$activities_def = array // nb: activity for any chani
(

	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("activity_ts","",		"1","3","","",	"","","",	"Sched Ts",""),
	array ("campaign_id","",		"1","2","","f", "","","",	"Campaign ID",""), 
	array ("contact_id","",			"1","2","","f", "","","",	"Contact ID",""), 

	array ("assigned_on","",		"1","3","","", "","","",	"Assigned On",""),
	array ("assigned_to_id","",		"1","2","","", "","","",	"Assigned To ID",""),
	array ("assigned_to","",		"1","2","","", "","","",	"Assigned To",""),
	array ("assigned_to_role","",		"1","2","","", "","","", 	"Assigned To Role",""),
		
	array ("src","",			"1","2","","",	"","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),
	array ("src_uid2","",			"1","2","","",	"","","", 	"Channel Uniqueid 2",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_usr","",			"1","2","","",	"","","", 	"Channel User",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),
	array ("src_ts","",			"1","2","","",	"","","", 	"Channel Timestamp",""),	
	array ("src_callid","",			"1","2","","",	"","","", 	"Channel Call ID",""),
	array ("src_campaign_id","",		"1","2","","",	"","","", 	"Channel Campaign ID",""),
	array ("src_action_id","",		"1","2","","",	"","","", 	"Channel Action ID",""),
	array ("src_status","",			"1","2","","",	"","","", 	"Channel Status",""),
	array ("src_status_ts","",		"1","3","","",	"","","", 	"Channel Status Ts",""),
	array ("src_status_duration","",	"1","4","","",	"","","", 	"Channel Status Duration",""),
	array ("src_end_ts","",			"1","3","","",	"","","", 	"Channel End Ts",""),
	array ("src_end_duration","",		"1","4","","",	"","","", 	"Channel Status Duration",""),
			
        array ("dispositions","",		"4","1","","",  "dispositions","GROUP_CONCAT(disposition)","",  "Disposition",""), 
	        
	array ("yr","",				"4","2","","",  "activities","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(src_ts)),'-01-01'))","",   "Year",":d:y:0: "), 
        array ("mn","",				"4","2","","",   "activities","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(src_ts)),'-',MONTH(FROM_UNIXTIME(src_ts)),'-01'))","",   "Month",":d:my:0: "), 
        array ("wk","",				"4","2","","",   "activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts))) - (DAYOFWEEK(FROM_UNIXTIME(src_ts))*86400)","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"4","2","","",   "activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts)))","",   "Date",":d:dmy:0: "), 
	array ("dth","",			"4","2","","",   "activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(src_ts))) + (HOUR(FROM_UNIXTIME(src_ts))*3600)","",   "Hour",":d:dmyh:0: "), 
        array ("h","hour",			"4","2","","",   "activities","HOUR(FROM_UNIXTIME(src_ts))","",   "Hour",""), 

	array ("activity","",                    "1","2","","",  "","","",       "Activity",""),
      array ("action","",                      "3","2","","",  "","","",       "Action","")

);

$dispositions_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
			
	array ("src","",			"1","2","","",	"","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),
	array ("src_uid2","",			"3","2","","",	"","","", 	"Channel Uniqueid 2",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_usr","",			"1","2","","",	"","","", 	"Channel User",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),
	array ("src_ts","",			"1","2","","",	"","","", 	"Channel Timestamp",""),	
	array ("src_callid","",			"1","2","","",	"","","", 	"Channel Call ID",""),
	array ("src_campaign_id","",		"1","2","","",	"","","", 	"Channel Campaign ID",""),
	array ("src_action_id","",		"1","2","","",	"","","", 	"Channel Action ID",""),

	array ("disposition_id","",		"3","2","m","f", "","","",	"Disposition",""), 
	array ("disposition","",		"3","2","","",  "","","",	"Disposition",""),  

	array ("src_uid_","",			"1","2","","",	"dispositions","'z'","", 		"Link UID",""),
	array ("src_uid2_","",			"1","2","","",	"dispositions","'z'","", 		"Link UID2",""),
	array ("is_active","",			"1","2","","",  "dispositions","'z'","", 		"Active",""),
	
	array ("has_contact","",		"1","2","","",  "","","", 				"has_contact",""),
		
	array ("reporter_id","",		"1","2","","f", "","","",				"Reporter ID",""),
	array ("reporter_contact_id","",	"1","2","","f",	"","","",				"Reporter Contact ID",""),
	array ("reporter_fullname","",		"3","1","","",  "reporters","contact_fullname","",	"Reporter Fullname",""),
	array ("reporter_phone","",		"3","2","","",  "reporters","contact_phone","",		"Reporter Phone",""),
	array ("reporter_email","",		"3","2","","",  "reporters","contact_email","",		"Reporter Email",""),
	array ("reporter_phone2","",		"3","2","","",  "reporters","contact_phone2","",	"Reporter Alternative Contact",""),
	array ("reporter_national_id","",	"3","2","","",  "reporters","contact_national_id","",	"Reporter National ID",""),
	array ("reporter_landmark","",		"3","2","","",  "reporters","contact_landmark","",	"Reporter Nearest Landmark",""),
	array ("reporter_dob","",		"3","3","","",  "reporters","contact_dob","",		"Reporter Date of Birth","d M Y H:i:s"),
	array ("reporter_age","",		"3","2","","",  "reporters","contact_age","",		"Reporter Age",""),
	array ("reporter_age_group_id","",	"3","2","","f",  "reporters","contact_age_group_id","",	"Reporter Age Group",""),
	array ("reporter_age_group","",		"3","2","","",  "reporters","contact_age_group","",	"Reporter Age Group",""),
	array ("reporter_sex_id","",		"3","2","","f", "reporters","contact_sex_id","",	"Reporter Gender",""),
	array ("reporter_sex","",		"3","2","","",  "reporters","contact_sex","",		"Reporter Gender",""),
	array ("reporter_national_id_type_id","","3","2","","", "reporters","contact_national_id_type_id","",	"ID Type ID",""),
	array ("reporter_national_id_type","",	"3","2","","",  "reporters","contact_national_id_type","",	"ID Type",""),
	array ("reporter_nationality_id","",	"3","2","","",  "reporters","contact_nationality_id","","Reporter Nationality ID",""),
	array ("reporter_nationality","",	"3","2","","",  "reporters","contact_nationality","",	"Reporter Nationality",""),
	array ("reporter_tribe_id","",		"3","2","","",  "reporters","contact_tribe_id","",	"Reporter Tribe ID",""),
	array ("reporter_tribe","",		"3","2","","",  "reporters","contact_tribe","",		"Reporter Tribe",""),
	array ("reporter_lang_id","",		"3","2","","",  "reporters","contact_lang_id","",	"Reporter Language ID",""),
	array ("reporter_lang","",		"3","2","","",  "reporters","contact_lang","",		"Reporter Language",""),
	array ("reporter_location_id","",	"3","2","","f",  "reporters","contact_location_id","",	"Reporter Location","",   "category","level","reporter_location_id_"),
	array ("reporter_location","",		"3","2","","",  "reporters","contact_location","",	"Reporter Location",""),
	array ("reporter_location_id_0","",	"3","2","","",  "reporters","contact_location_id_0","",	"Reporter Region ID",""),
	array ("reporter_location_id_1","",	"3","2","","",  "reporters","contact_location_id_1","",	"Reporter District ID",""),
	array ("reporter_location_id_2","",	"3","2","","",  "reporters","contact_location_id_2","",	"Reporter County ID",""),
	array ("reporter_location_id_3","",	"3","2","","",  "reporters","contact_location_id_3","",	"Reporter Sub County ID",""),
	array ("reporter_location_id_4","",	"3","2","","",  "reporters","contact_location_id_4","",	"Reporter Parish ID",""),
	array ("reporter_location_id_5","",	"3","2","","",  "reporters","contact_location_id_5","",	"Reporter Village ID",""),
	array ("reporter_location_0","",	"3","2","","",  "reporters","contact_location_0","",	"Reporter Region",""),
	array ("reporter_location_1","",	"3","2","","",  "reporters","contact_location_1","",	"Reporter District",""),
	array ("reporter_location_2","",	"3","2","","",  "reporters","contact_location_2","",	"Reporter County",""),
	array ("reporter_location_3","",	"3","2","","",  "reporters","contact_location_3","",	"Reporter Sub County",""),
	array ("reporter_location_4","",	"3","2","","",  "reporters","contact_location_4","",	"Reporter Parish",""),
	array ("reporter_location_5","",	"3","2","","",  "reporters","contact_location_5","",	"Reporter Village",""),
	
	 array ("case_id","",                    "1","2","","f", "","","",       "Case ID",""), 
        array ("case_category","",              "3","2","","",  "","","",       "Case Category",""),
        array ("case_priority","",              "3","2","","",  "","","",       "Case Priority",""),
        array ("case_status","",                "3","2","","",  "","","",       "Case Status",""),

);

$actions_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("action","",			"1","2","","",	"","","",	"Action",""),
	array ("campaign_id","",		"1","2","","f", "","","",	"Campaign ID",""), 
	array ("contact_id","",			"1","2","","f", "","","",	"Contact ID",""), 
	array ("case_id","",			"1","2","","f", "","","",	"Case ID",""), 

	array ("assigned_to_id","",		"1","2","","f", "","","",	"Assigned To ID",""),
	array ("assigned_to","",		"1","2","","", "","","",	"Assigned To",""),
	array ("assigned_to_role","",		"1","2","","", "","","", 	"Assigned To Role",""),

	array ("src","",			"1","2","","",	"","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),
	array ("src_uid2","",			"1","2","","",	"","","", 	"Channel Uniqueid 2",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_usr","",			"1","2","","",	"","","", 	"Channel User",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),
	array ("src_ts","",			"1","2","","",	"","","", 	"Channel Timestamp",""),	
	array ("src_callid","",			"1","2","","",	"","","", 	"Channel Call ID",""),
	array ("src_campaign_id","",		"1","2","","",	"","","", 	"Channel Campaign ID",""),
	array ("src_action_id","",		"1","2","","",	"","","", 	"Channel Action ID",""),

	array ("disposition_id","",		"1","2","","f", "","","",	"Disposition ID",""), 
	array ("disposition","",		"1","2","","",  "","","",	"Disposition",""),  
	array ("detail","",			"1","1","","",  "","","",	"Detail",""),  
);

$attachments_def = array // 
(
	array ("id","",				"1","2","","", "","","", 	"ID",""),
	array ("created_on","",			"0","3","","", "","","", 	"Created On",""),
	array ("created_by","",			"0","2","","", "","","", 	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	 "Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
	
	array ("file_id","",			"1","2","m","f", "","","", 	"File ID",""),
	array ("file_name","",			"1","2","","", "","","", 	"Name",""),
	array ("file_mime","",			"1","2","","",	"","","", 	"Mime",""),
	array ("file_size","",			"1","2","","", 	"","","", 	"Size",""),
	array ("file_uploadstatus","",		"1","2","","", 	"","","", 	"Upload Status",""),
	array ("file_movestatus","",		"1","2","","", 	"","","", 	"Move Status",""),

	array ("pos","i_",			"3","2","","", "","","",	"Position",""), 
	//array ("source","",			"1","2","","", "","","",	"Source",""), 
	//array ("source_id","",		"1","2","","f", "","","",	"Source",""), 
	array ("case_id","",			"1","2","","f", "","","",	"Case ID",""),
	array ("case_id_","",			"3","2","","", "","","",	"Link ID",""),		
);

// ------------------------------

$reporters_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
	
	array ("contact_id","",			"1","2","m","f", "","","",	"Contact",""),
	array ("contact_fullname","",		"3","1","","", "","","",	"Fullname",""),
	array ("contact_fname","",		"3","1","","", "","","",	"First Name",""),
	array ("contact_lname","",		"3","1","","",  "","","",	"Last Name",""),
	array ("contact_phone","",		"3","2","","", "","","",	"Phone",""),
	array ("contact_email","",		"3","2","","", "","","",	"Email",""),
	array ("contact_phone2","",		"3","2","","", "","","",	"Alternative Contact",""),
	array ("contact_dob","",		"3","3","","", "","","",	"Date of Birth","d M Y H:i:s"),
	array ("contact_age","",		"3","2","","", "","","",	"Age",""),
	array ("contact_age_group_id","",	"3","2","","f", "","","",	"Age Group ID",""),
	array ("contact_age_group","",		"3","2","","", "","","",	"Age Group",""),
	array ("contact_sex_id","",		"3","2","","f", "","","",	"Gender ID",""),
	array ("contact_sex","",		"3","2","","", "","","",	"Gender",""),
	array ("contact_national_id_type_id","","3","2","","", "","","",	"ID Type",""),
	array ("contact_national_id_type","",	"3","2","","", "","","",	"ID Type",""),
	array ("contact_national_id","",	"3","2","","", "","","",	"National ID",""),
	array ("contact_address","",		"3","1","","", "","","",	"Address",""),
	array ("contact_residence","",		"3","2","","", "","","",	"Residence",""),
	array ("contact_nationality_id","",	"3","2","","f", "","","",	"Nationality ID",""),
	array ("contact_nationality","",	"3","2","","", "","","",	"Nationality",""),
	array ("contact_tribe_id","",		"3","2","","f", "","","",	"Tribe ID",""),
	array ("contact_tribe","",		"3","2","","", "","","",	"Tribe",""),
	array ("contact_lang_id","",		"3","2","","f", "","","",	"Language ID",""),
	array ("contact_lang","",		"3","2","","", "","","",	"Language",""),
	// array ("contact_location_id","",	"3","2","","f", "","","",	"Location ID",""),
	array ("contact_location_id","",	"3","2","","f", "","","",	"Location ID","",	"category","level","contact_location_id_"),
	array ("contact_location","",		"3","2","","", "","","",	"Location",""),
	array ("contact_landmark","",		"3","2","","", "","","",	"Nearest Landmark",""),
	array ("contact_location_id_0","",	"3","2","","", "","","",	"Location Level 0 ID",""),
	array ("contact_location_id_1","",	"3","2","","", "","","",	"Location Level 1 ID",""),
	array ("contact_location_id_2","",	"3","2","","", "","","",	"Location Level 2 ID",""),
	array ("contact_location_id_3","",	"3","2","","", "","","",	"Location Level 3 ID",""),
	array ("contact_location_id_4","",	"3","2","","", "","","",	"Location Level 4 ID",""),
	array ("contact_location_id_5","",	"3","2","","", "","","",	"Location Level 5 ID",""),
	array ("contact_location_id_6","",	"3","2","","", "","","",	"Location Level 6 ID",""),
	array ("contact_location_0","",		"3","2","","", "","","",	"Location Level 0",""),
	array ("contact_location_1","",		"3","2","","", "","","",	"Location Level 1",""),
	array ("contact_location_2","",		"3","2","","", "","","",	"Location Level 2",""),
	array ("contact_location_3","",		"3","2","","", "","","",	"Location Level 3",""),
	array ("contact_location_4","",		"3","2","","", "","","",	"Location Level 4",""),
	array ("contact_location_5","",		"3","2","","", "","","",	"Location Level 5",""),
	array ("contact_location_6","",		"3","2","","", "","","",	"Location Level 6",""),
	array ("contact_is_refugee","",		"3","2","","", "","","",	"Reporter Is Refugee","::yesno:0:2"),
		
	array ("src","",			"1","2","m","","","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),
	
	array ("is_client","",			"4","2","","",	"clients","IF(COUNT(id)>0,'1','')","", 	"Is Client",""),

	array ("case_id","",			"1","2","","f", "","","",	"Case ID",""),  // link once
);

$perpetrators_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
	
	array ("case_id","",			"1","2","","f", "","","",	"Case ID",""),  // link once

	array ("contact_id","",			"3","2","m","f", "","","",	"Contact ID",""),
	array ("contact_fullname","",		"3","1","","", "","","",	"Perp Fullname",""),
	array ("contact_fname","",		"3","1","m","", "","","",	"First Name",""),
	array ("contact_lname","",		"3","1","","",  "","","",	"Last Name",""),
	array ("contact_phone","",		"3","2","","", "","","",	"Perp Phone",""), // todo: regex
	array ("contact_email","",		"3","2","","", "","","",	"Perp Email",""),
	array ("contact_phone2","",		"3","2","","", "","","",	"Perp Alternative Contact",""),
	array ("contact_dob","",		"3","3","","", "","","",	"Perp Date of Birth","d M Y H:i:s"),
	array ("contact_age","",		"3","2","","", "","","",	"Perp Age",""),
	array ("contact_age_group_id","",	"3","2","","f", "","","",	"Age Group ID",""),
	array ("contact_age_group","",		"3","2","","", "","","",	"Perp Age Group",""),
	array ("contact_sex_id","",		"3","2","","f", "","","",	"Gender ID",""),
	array ("contact_sex","",		"3","2","","", "","","",	"Perp Gender",""),
	array ("contact_national_id_type_id","","3","2","","", "","","",	"ID Type",""),
	array ("contact_national_id_type","",	"3","2","","", "","","",	"Perp ID Type",""),
	array ("contact_national_id","",	"3","2","","", "","","",	"Perp National ID",""),
	array ("contact_address","",		"3","1","","", "","","",	"Perp Address",""),
	array ("contact_residence","",		"3","2","","", "","","",	"Perp Residence",""),
	array ("contact_nationality_id","",	"3","2","","f", "","","",	"Nationality ID",""),
	array ("contact_nationality","",	"3","2","","", "","","",	"Perp Nationality",""),
	array ("contact_tribe_id","",		"3","2","","f", "","","",	"Tribe ID",""),
	array ("contact_tribe","",		"3","2","","", "","","",	"Perp Tribe",""),
	array ("contact_lang_id","",		"3","2","","f", "","","",	"Language ID",""),
	array ("contact_lang","",		"3","2","","", "","","",	"Perp Language",""),
	array ("contact_location_id","",	"3","2","","f", "","","",	"Location ID","",	"category","level","contact_location_id_"),
	array ("contact_location","",		"3","2","","", "","","",	"Perp Location",""),
	array ("contact_landmark","",		"3","2","","", "","","",	"Perp Nearest Landmark",""),
	array ("contact_location_id_0","",	"3","2","","", "","","",	"Perp Region ID",""),
	array ("contact_location_id_1","",	"3","2","","", "","","",	"Perp District ID",""),
	array ("contact_location_id_2","",	"3","2","","", "","","",	"Perp County ID",""),
	array ("contact_location_id_3","",	"3","2","","", "","","",	"Perp Sub County ID",""),
	array ("contact_location_id_4","",	"3","2","","", "","","",	"Perp Parish ID",""),
	array ("contact_location_id_5","",	"3","2","","", "","","",	"Perp Village ID",""),
	array ("contact_location_id_6","",	"3","2","","", "","","",	"Perp Village ID",""),
	array ("contact_location_0","",		"3","2","","", "","","",	"Perp Region",""),
	array ("contact_location_1","",		"3","2","","", "","","",	"Perp District",""),
	array ("contact_location_2","",		"3","2","","", "","","",	"Perp County",""),
	array ("contact_location_3","",		"3","2","","", "","","",	"Perp SubCounty",""),
	array ("contact_location_4","",		"3","2","","", "","","",	"Perp Parish",""),
	array ("contact_location_5","",		"3","2","","", "","","",	"Perp Village",""),
	array ("contact_location_6","",		"3","2","","", "","","",	"Perp Constituency",""),
	array ("contact_is_refugee","",		"3","2","","", "","","",	"Perp Is Refugee","::yesno:0:2"),
			
	array ("relationship_id","",		"3","2","","f", "","","",	"Perp Relationship with Client ID",""),
	array ("relationship","",		"3","2","","", "","","",	"Perp Relationship with Client",""),
	array ("shareshome_id","",		"3","2","","f", "","","",	"Shares Home ID",""),
	array ("shareshome","",			"3","2","","", "","","",	"Perp Shares Home",""),
	array ("marital_id","",			"3","2","","f", "","","",	"Marital Status ID",""),
	array ("marital","",			"3","2","","", "","","",	"Perp Marital Status",""),
	array ("health_id","",			"3","2","","f", "","","",	"Health Status ID",""),
	array ("health","",			"3","2","","", "","","",	"Perp Health Status",""),
	array ("employment_id","",		"3","2","","f", "","","",	"Employment Status ID",""),
	array ("employment","",			"3","2","","", "","","",	"Perp Employment Status",""),
	array ("guardian_fullname","",		"3","1","","", "","","",	"Perp Guardian Name",""),
	array ("notes","",			"3","1","","", "","","",	"Perp Additional Details",""),	

	array ("spouse_profession_id","",	"3","2","","f", "","","",	"Spouse Profession ID",""),
	array ("spouse_profession","",		"3","2","","", "","","",	"Client Spouse Profession",""),
	array ("spouse_fullname","",		"3","1","","", "","","",	"Client Spouse Fullname",""),

	
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),	
	
	array ("is_delete","",			"3","2","v","", "","0","",	"Client Is Deleted",""),
	array ("case_id_","",			"3","2","","", "","","",	"Case Link ID",""),
);

$clients_def = array 
(
	array ("id","",				"0","2","","", "","","",	"",""),
	array ("created_on","",			"0","3","","", "","","",	"",""),
	array ("created_by","",			"0","2","","", "","","",	"",""),
	array ("created_by_id","",		"0","2","","", "","","",	"",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),
	
	array ("case_id","",			"1","2","","f", "","","",	"Case ID",""),  // link once

	array ("contact_id","",			"3","2","m","f", "","","",	"Contact ID",""),
	array ("contact_fullname","",		"3","1","","", "","","",	"Client Fullname",""),
	array ("contact_fname","",		"3","1","m","", "","","",	"First Name",""),
	array ("contact_lname","",		"3","1","","",  "","","",	"Last Name",""),
	array ("contact_phone","",		"3","2","","", "","","",	"Client Phone",""), // todo: regex
	array ("contact_email","",		"3","2","","", "","","",	"Client Email",""),
	array ("contact_phone2","",		"3","2","","", "","","",	"Client Alternative Contact",""),
	array ("contact_dob","",		"3","3","","", "","","",	"Client Date of Birth","d M Y H:i:s"),
	array ("contact_age","",		"3","2","","", "","","",	"Client Age",""),
	array ("contact_age_group_id","",	"3","2","","f", "","","",	"Age Group ID",""),
	array ("contact_age_group","",		"3","2","","", "","","",	"Client Age Group",""),
	array ("contact_sex_id","",		"3","2","","f", "","","",	"Gender ID",""),
	array ("contact_sex","",		"3","2","","", "","","",	"Client Gender",""),
	array ("contact_national_id_type_id","","3","2","","", "","","",	"ID Type ID",""),
	array ("contact_national_id_type","",	"3","2","","", "","","",	"Client ID Type",""),
	array ("contact_national_id","",	"3","2","","", "","","",	"Client National ID",""),
	array ("contact_address","",		"3","1","","", "","","",	"Client Address",""),
	array ("contact_residence","",		"3","2","","", "","","",	"Client Residence",""),
	array ("contact_nationality_id","",	"3","2","","f", "","","",	"Nationality ID",""),
	array ("contact_nationality","",	"3","2","","", "","","",	"Client Nationality",""),
	array ("contact_tribe_id","",		"3","2","","f", "","","",	"Tribe ID",""),
	array ("contact_tribe","",		"3","2","","", "","","",	"Client Tribe",""),
	array ("contact_lang_id","",		"3","2","","f", "","","",	"Language ID",""),
	array ("contact_lang","",		"3","2","","", "","","",	"Client Language",""),
	array ("contact_location_id","",	"3","2","","f", "","","",	"Location ID","",	"category","level","contact_location_id_"),
	array ("contact_location","",		"3","2","","", "","","",	"Client Location",""),
	array ("contact_landmark","",		"3","2","","", "","","",	"Client Nearest Landmark",""),
	array ("contact_location_id_0","",	"3","2","","", "","","",	"Client Region ID",""),
	array ("contact_location_id_1","",	"3","2","","", "","","",	"Client District ID",""),
	array ("contact_location_id_2","",	"3","2","","", "","","",	"Client County ID",""),
	array ("contact_location_id_3","",	"3","2","","", "","","",	"Client Sub County ID",""),
	array ("contact_location_id_4","",	"3","2","","", "","","",	"Client Parish ID",""),
	array ("contact_location_id_5","",	"3","2","","", "","","",	"Client Village ID",""),
	array ("contact_location_id_6","",	"3","2","","", "","","",	"Client Constituency ID",""),
	array ("contact_location_0","",		"3","2","","", "","","",	"Client Region",""),
	array ("contact_location_1","",		"3","2","","", "","","",	"Client District",""),
	array ("contact_location_2","",		"3","2","","", "","","",	"Client County",""),
	array ("contact_location_3","",		"3","2","","", "","","",	"Client SubCounty",""),
	array ("contact_location_4","",		"3","2","","", "","","",	"Client Parish",""),
	array ("contact_location_5","",		"3","2","","", "","","",	"Client Village",""),
	array ("contact_location_6","",		"3","2","","", "","","",	"Client Constituency",""),
	array ("contact_is_refugee","",		"3","2","","", "","","",	"Client Is Refugee","::yesno:0:2"),
	
	array ("is_reporter","",		"4","2","","", "reporters","IF(COUNT(id)>0,'1','')","",	"Is Reporter","::yesno:0:1"),

	array ("category_id","",		"3","2","","f", "","","",	"Category ID",""), 	// todo: multiple categories
	array ("category","",			"3","2","","", "","","",	"Category",""),	
	array ("gbv_related","",		"3","2","","", "","","",	"GBV Related","::yesno:0:2"),	// if not set by set automaticaly if age>17
	
	array ("relationship_id","",		"3","2","","f", "","","",	"Report Relationship to Client ID",""),
	array ("relationship","",		"3","2","","", "","","",	"Report Relationship to Client",""),
	array ("relationship_comment","",	"3","1","","", "","","",	"Relationship Comment",""),

	array ("is_disabled","",		"3","2","","", "","","",	"Client IsDisability","::yesno:0:1"),
	array ("disability_id","",		"3","2","","f", "","","",	"Disability ID",""),
	array ("disability","",			"3","2","","", "","","",	"Client Disability",""),
	array ("health_id","",			"3","2","","f", "","","",	"Health Status ID",""),
	array ("health","",			"3","2","","", "","","",	"Client Health Status",""),
	array ("hiv_id","",			"3","2","","f", "","","",	"HIV ID",""),
	array ("hiv","",			"3","2","","", "","","",	"Client HIV",""),
	array ("special_services","",		"3","1","","", "","","",	"Client Registered for Special Services",""),

	array ("in_school","",			"3","2","","", "","","",	"Client In School","::yesno:0:1"),
	array ("school_type_id","",		"3","2","","f", "","","",	"School Type ID",""),
	array ("school_type","",		"3","2","","", "","","",	"Client School Type",""),
	array ("school_level_id","",		"3","2","","f", "","","",	"School Level ID",""),
	array ("school_level","",		"3","2","","", "","","",	"Client School Level",""),
	array ("school_attendance","",		"3","1","","", "","","",	"Client School Attendance",""),	
	array ("school_name","",		"3","1","","", "","","",	"Client School Name",""),	
	array ("school_address","",		"3","1","","", "","","",	"Client School Address",""),	

	array ("not_in_school_id","",		"3","2","","f", "","","",	"Reason for not attending School ID",""),
	array ("not_in_school","",		"3","2","","", "","","",	"Client Reason for not attending School",""),
	array ("not_in_school_reason","",	"3","1","","", "","","",	"Client Not In School Reason",""),	
	
	array ("is_married","",			"3","2","","", "","","",	"Client Is Married","::yesno:0:1"),
	array ("marital_id","",			"3","2","","f", "","","",	"Marital Status ID",""),
	array ("marital","",			"3","2","","", "","","",	"Client Marital Status",""),
	array ("spouse_profession_id","",	"3","2","","f", "","","",	"Spouse Profession ID",""),
	array ("spouse_profession","",		"3","2","","", "","","",	"Client Spouse Profession",""),
	array ("spouse_fullname","",		"3","1","","", "","","",	"Client Spouse Fullname",""),

	array ("is_guardian_known","",		"3","2","","", "","","",	"Client Is Guardian Known?","::yesno:0:1"),
	array ("guardian_marital_id","",	"3","2","","f", "","","",	"Guardian's Marital Status ID",""),
	array ("guardian_marital","",		"3","2","","", "","","",	"Client Guardian's Marital Status",""),
	array ("guardian_fullname","",		"3","1","","", "","","",	"Client Guardian's Name",""),
	array ("guardian_national_id","",	"3","1","","", "","","",	"Client Guardian's National ID",""),

	array ("household_id","",		"3","2","","f", "","","",	"Household Type ID",""),
	array ("household","",			"3","2","","", "","","",	"Client Household Type",""),	
	array ("household_adults","",		"3","4","","", "","","",	"Client Number of Adults in Household",""),	
	array ("household_head_occupation_id","","3","2","","f", "","","",	"Client Occupation of Household Head ID",""),	
	array ("household_head_occupation","",	"3","2","","", "","","",	"Client Occupation of Household Head",""),	
	
	array ("is_disabled_refered","",	"3","2","","", "","","",	"Refered for Special services","::yesno:0:1"),	
	array ("is_disabled_referals","",	"4","1","","",	"client_referals","GROUP_CONCAT(CONCAT(category_id,':',category_name))","",	"Referals",""),	
	
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),	
	
	array ("is_delete","",			"3","2","v","", "","0","",	"Client Is Deleted",""),
	
	array ("is_reporter_id","",		"3","2","","", "","","",	"Is Reporter ID",""),
	array ("case_uuid","",			"1","2","","", "","","",	"Case UUID",""),
	array ("case_id_","",			"3","2","","", "","","",	"Case Link ID",""),
);

$services_def = array 
(
	array ("id","",				"0","2","","", "","","",	"ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On",""),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("case_id","",			"1","2","m","f",	"","","", 	"Case ID",""), 		// 
	array ("case_id_","",			"3","2","","", "","","",	"Case Link ID",""),
	array ("ca_id","",			"1","2","","",	"","","", 	"Case Update ID",""), 		
	array ("category_id","",		"1","2","m","f",	"","","",	"Service ID",""), 
	array ("category_name","",		"1","2","","",	"","","", 	"Service Offered",""),
	array ("category_fullname","",		"1","2","","",	"","","", 	"Fullname",""),
	array ("category_fullname_id","",	"1","1","","",	"","","", 	"Fullname ID",""), 
);

$referals_def = array 
(
	array ("id","",				"0","2","","", "","","",	"ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On",""),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("case_id","",			"1","2","m","f",	"","","", 	"Case ID",""), 		// 
	array ("case_id_","",			"3","2","","", "","","",	"Case Link ID",""),
	array ("ca_id","",			"1","2","","",	"","","", 	"Case Update ID",""), 		
	array ("category_id","",		"1","2","m","f",	"","","",	"Service ID",""), 
	array ("category_name","",		"1","2","","",	"","","", 	"Service Offered",""),
	array ("category_fullname","",		"1","2","","",	"","","", 	"Fullname",""),
	array ("category_fullname_id","",	"1","1","","",	"","","", 	"Fullname ID",""), 
);

$client_referals_def = array 
(
	array ("id","",				"0","2","","", "","","",	"ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On",""),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("client_id","",			"1","2","m","f",	"","","", 	"Client ID",""), 		// 
	array ("client_id_","",			"3","2","","",	"","","", 	"Client Link ID",""), 		
	array ("ca_id","",			"1","2","","",	"","","", 	"Case Update ID",""), 		
	array ("category_id","",		"1","2","m","f",	"","","",	"Service ID",""), 
	array ("category_name","",		"1","2","","",	"","","", 	"Service Offered",""),
	array ("category_fullname","",		"1","2","","",	"","","", 	"Fullname",""),
	array ("category_fullname_id","",	"1","1","","",	"","","", 	"Fullname ID",""), 
);

$cases_def = array 
(
	array ("id","",				"0","2","","", "","","",	"CASE ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On","d M Y H:i:s"),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role","::role:0:1"),

	array ("gbv_related","",		"3","2","m","", "","","", 	"GBV Related","::yesno:0:2"),

	array ("case_category_id","",		"3","2","m","f","","","",  	"Case Category ID","",   "category","level","cat_id_"),	
	array ("case_category","",		"3","2","","", "","","", 	"Case Category",""),
	array ("case_category_root_id","",	"3","2","","", "","","",	"Case Category Root ID",""),
	array ("case_category_fullname_id","",	"3","2","","", "","","",	"Case Category Fullname ID",""),
	array ("cat_id_0","",			"3","2","","", "","","",	"Case Type",""),
	array ("cat_id_1","",			"3","2","","", "","","",	"Main Category",""),
	array ("cat_id_2","",			"3","2","","", "","","",	"Sub Category 1 ID",""),
	array ("cat_id_3","",			"3","2","","", "","","",	"Sub Category 2 ID",""),
	array ("cat_id_4","",			"3","2","","", "","","",	"Sub Category 3 ID",""),
	array ("cat_0","",			"3","2","","", "","","",	"Case Type",""),
	array ("cat_1","",			"3","2","","", "","","",	"Main Category",""),
	array ("cat_2","",			"3","2","","", "","","",	"Sub Category 1",""),
	array ("cat_3","",			"3","2","","", "","","",	"Sub Category 2",""),
	array ("cat_4","",			"3","2","","", "","","",	"Sub Category 3",""),
	
	array ("knowabout116_id","",		"3","2","","f", "","","",	"Know about 116 Id",""),
	array ("knowabout116","",		"3","2","","",  "","","",	"Know about 116",""),					
	array ("justice_id","",			"3","2","","f",	"","","", 	"Justice ID",""), 
	array ("justice","",			"3","2","","",	"","","", 	"Justice",""),
	array ("assessment_id","",		"3","2","","f",	"","","", 	"Assessment ID",""),
	array ("assessment","",			"3","2","","",	"","","", 	"Assessment",""),
				
	array ("escalated_by_id","",		"3","2","","f",	"","","",	"Escalated By ID",""),
	array ("escalated_by","",		"3","2","","f",	"","","",	"Escalated By",""),
	array ("escalated_by_role","",		"3","2","","f",	"","","",	"Escalated By Role",""),

	array ("escalated_to_id","",		"3","2","","f",	"","","",	"Escalated To ID",""),
	array ("escalated_to","",		"3","2","","",	"","","", 	"Escalated To",""),	
	array ("escalated_to_role","",		"3","2","","",	"","","", 	"Escalated To Role",""),
	
	array ("assigned_to_id","",		"3","2","","",	"","","", 	"Assigned To ID",""),	
	array ("assigned_to","",		"3","2","","",	"","","", 	"Assigned To",""),	
	array ("assigned_to_role","",		"3","2","","",	"","","", 	"Assigned To Role",""),	
	
	array ("priority","",			"3","2","m","",	"","","", 	"Priority","::case_priority:0:1"), 
	array ("status","",			"3","2","m","",	"","","", 	"Status","::case_status:0:1"),

	array ("services","",			"4","1","","",	"services","GROUP_CONCAT(CONCAT(category_id,':',category_name))","",	"Services Offered",""),
	array ("referals","",			"4","1","","",	"referals","GROUP_CONCAT(CONCAT(category_id,':',category_name))", "",	"Referals", ""),

	array ("narrative","",			"3","1","m","",	"","","", 	"Narrative",""), 		
	array ("plan","",			"3","1","m","",	"","","", 	"Plan",""), 	

	array ("police_ob_no","",		"3","2","","",  "","","",	"Police Ref Number",""),
	array ("specify_service","",		"3","2","","",  "","","",	"Specify Service",""),
	array ("specify_referal","",		"3","2","","",  "","","",	"Specify Referal",""),

	array ("is_medical_exam_done","",	"3","2","","",  "","","",	"Is Medical Exam Done?","::yesno:0:1"),
	array ("is_incidence_reported","",	"3","2","","",  "","","",	"Is Incidence Reported?","::yesno:0:1"),
	array ("is_hiv_tested","",		"3","2","","",  "","","",	"Is HIV Tested?","::yesno:0:1"),
	array ("is_pep_given","",		"3","2","","",  "","","",	"Is PEP Given?","::yesno:0:1"),
	array ("is_art_given","",		"3","2","","",  "","","",	"Is ART Given?","::yesno:0:1"),
	array ("is_ecp_given","",		"3","2","","",  "","","",	"Is ECP Given?","::yesno:0:1"),
	array ("is_counselling_given","",	"3","2","","",  "","","",	"Is Counselling Given?","::yesno:0:1"),
	
	array ("incidence_when","",		"3","3","","", "","","",	"Date of Incident","d M Y H:i:s"),
	array ("incidence_location","",		"3","1","","", "","","",	"Incidence Reported Where",""),
	array ("incidence_ref_no","",		"3","1","","", "","","",	"Incidence Police Ref. No.",""),
	array ("hiv_test_result","",		"3","2","","", "","","",	"HIV Test Result","::charge:0:1"),
	array ("counseling_org","",		"3","2","","", "","","",	"Counseling Organisation",""),	
 
 	array ("src","",			"1","2","","",	"","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel Uniqueid",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),

	array ("reporter_id","",		"1","2","m","f","","","",	"Reporter ID",""),
	array ("reporter_contact_id","",	"1","2","m","f","","","",	"Reporter Contact ID",""),
	array ("reporter_fullname","",		"3","1","m","",  "","","",	"Reporter Fullname",""),
	array ("reporter_phone","",		"3","2","","",  "","","",	"Reporter Phone",""),
	array ("reporter_email","",		"3","2","","",  "","","",	"Reporter Email",""),
	array ("reporter_phone2","",		"3","2","","",  "","","",	"Reporter Alternative Contact",""),
	array ("reporter_national_id","",	"3","2","","",  "","","",	"Reporter National ID",""),
	array ("reporter_landmark","",		"3","2","","",  "","","",	"Reporter Nearest Landmark",""),
	array ("reporter_dob","",		"3","3","","",  "","","",	"Reporter Date of Birth","d M Y H:i:s"),
	array ("reporter_age","",		"3","2","","",  "","","",	"Reporter Age",""),
	array ("reporter_age_group_id","",	"3","2","m","",  "","","",	"Reporter Age Group",""),
	array ("reporter_age_group","",		"3","2","","",  "","","",	"Reporter Age Group",""),
	array ("reporter_sex_id","",		"3","2","m","",  "","","",	"Reporter Gender",""),
	array ("reporter_sex","",		"3","2","","",  "","","",	"Reporter Gender",""),
	array ("reporter_national_id_type_id","","3","2","","", "","","",	"ID Type ID",""),
	array ("reporter_national_id_type","",	"3","2","","",  "","","",	"ID Type",""),
	array ("reporter_nationality_id","",	"3","2","","",  "","","",	"Reporter Nationality ID",""),
	array ("reporter_nationality","",	"3","2","","",  "","","",	"Reporter Nationality",""),
	array ("reporter_tribe_id","",		"3","2","","",  "","","",	"Reporter Tribe ID",""),
	array ("reporter_tribe","",		"3","2","","",  "","","",	"Reporter Tribe",""),
	array ("reporter_lang_id","",		"3","2","","",  "","","",	"Reporter Language ID",""),
	array ("reporter_lang","",		"3","2","","",  "","","",	"Reporter Language",""),
	array ("reporter_location_id","",	"3","2","","",  "","","",	"Reporter Location ID","",   "category","level","reporter_location_id_"),
	array ("reporter_location","",		"3","2","","",  "","","",	"Reporter Location",""),
	array ("reporter_location_id_0","",	"3","2","","",  "","","",	"Reporter Region ID",""),
	array ("reporter_location_id_1","",	"3","2","","",  "","","",	"Reporter District ID",""),
	array ("reporter_location_id_2","",	"3","2","","",  "","","",	"Reporter County ID",""),
	array ("reporter_location_id_3","",	"3","2","","",  "","","",	"Reporter Sub County ID",""),
	array ("reporter_location_id_4","",	"3","2","","",  "","","",	"Reporter Parish ID",""),
	array ("reporter_location_id_5","",	"3","2","","",  "","","",	"Reporter Village ID",""),
	array ("reporter_location_0","",	"3","2","","",  "","","",	"Reporter Region",""),
	array ("reporter_location_1","",	"3","2","","",  "","","",	"Reporter District",""),
	array ("reporter_location_2","",	"3","2","","",  "","","",	"Reporter County",""),
	array ("reporter_location_3","",	"3","2","","",  "","","",	"Reporter Sub County",""),
	array ("reporter_location_4","",	"3","2","","",  "","","",	"Reporter Parish",""),
	array ("reporter_location_5","",	"3","2","","",  "","","",	"Reporter Village",""),
	array ("reporter_is_refugee","",	"3","2","","", "","","",	"Reporter Is Refugee","::yesno:0:1"),
	
	array ("client_count","",		"4","4","v","",  "","","",	"Client Count",""), 
	array ("perp_count","",			"4","4","v","",  "","","",	"Perpetrator Count",""), 
			
	array ("is_reporter_client","",         "4","2","","",  "clients","MAX(IF(is_reporter=1,1,0))","",      "Is Reporter Client?","::yesno:0:1"),
	
	array ("activity_count","",		"4","4","","",	"dispositions","COUNT(id)","", 			"Activity Count",""),
	array ("activity_ids","",		"4","1","","",	"dispositions","GROUP_CONCAT(id)","", 		"Activity IDs",""),
	array ("activity_last_id","",		"4","2","","f",	"dispositions","MAX(id)","activity_last_id", 	"Last Activity ID",""),

	array ("activity_on","",		"5","3","","",	"dispositions","created_on","", 			"Last Activity On",""),	
	array ("activity_by","",		"5","2","","",	"dispositions","created_by","", 			"Last Activity By",""),	
	array ("activity_by_id","",		"5","2","","",	"dispositions","created_by_id","", 			"Last Activity By ID",""),	
	array ("activity_by_role","",		"5","2","","",	"dispositions","created_by_role","", 		"Last Activity By Role",""),	
	array ("activity_src","",		"5","2","","",	"dispositions","src","", 				"Last Activity Source",""), 	
	array ("activity_src_uid","",		"5","2","","",	"dispositions","src_uid","", 			"Last Activity Source UID",""), 	
	array ("disposition_id","",		"3","2","","f", "dispositions","disposition_id","",			"Disposition ID",""), 
	array ("disposition","",		"3","2","","",  "dispositions","disposition","",			"Disposition",""),  
	
	array ("final_status","",		"4","2","","",   "cases","IF(status!=2 && escalated_to_id>0,3,status)","",	"Final Status",""), 
 
	array ("yr","",				"4","2","","",   "cases","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(created_on)),'-01-01'))","",   "Year",":d:y:0: "), 
        array ("mn","",				"4","2","","",   "cases","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(created_on)),'-',MONTH(FROM_UNIXTIME(created_on)),'-01'))","",   "Month",":d:my:0: "), 
        array ("wk","",				"4","2","","",   "cases","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on))) - (DAYOFWEEK(FROM_UNIXTIME(created_on))*86400)","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"4","2","","",   "cases","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on)))","",   "Date",":d:dmy:0: "), 
	array ("hr","",				"4","2","","",   "cases","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on))) + (HOUR(FROM_UNIXTIME(created_on))*3600)","",   "Hour",":d:dmyh:0: "), 
        array ("h","",				"4","2","","",   "cases","HOUR(FROM_UNIXTIME(created_on))","",   	"Hour",""), 

	array ("mn_closed","",			"4","2","","", "case_activities","MIN(IF(status=2,mn,NULL))","",	"",""),
);

$case_activities_def = array 
(
	array ("id","",				"0","2","","", "","","",	"ID",""),
	array ("created_on","",			"0","3","","", "","","",	"Created On",""),
	array ("created_by","",			"0","2","","", "","","",	"Created By",""),
	array ("created_by_id","",		"0","2","","", "","","",	"Created By ID",""),
	array ("created_by_role","",		"0","2","","", "","","", 	"Created By Role",""),

	array ("case_id","",			"1","2","","",	"","","", 	"Case ID",""), 	
	array ("aub_id","",			"1","2","","",	"","","", 	"Case ID",""), 	
	array ("activity","",			"1","2","","",	"","","", 	"Activity",""), 		
	array ("activity_ref","",		"1","2","","",	"","","", 	"Activity",""), 		
	array ("detail","",			"1","1","","",	"","","", 	"Detail",""), 				
	array ("priority","",			"1","2","","",	"","","", 	"Priority",""), 
	array ("status","",			"1","2","","",	"","","", 	"Status",""), 		
	array ("escalated_to_id","",		"1","2","","f",	"","","",	"Escalated To ID",""),
	array ("escalated_to","",		"1","2","","",	"","","", 	"Escalated To",""),	
	array ("escalated_to_role","",		"1","2","","",	"","","", 	"Escalated To Role",""),
	array ("disposition_id","",		"1","2","","",  "","","",	"Disposition ID",""),  // for case only
	array ("disposition","",		"1","2","","",  "","","",	"Disposition",""),  
				
	array ("src","",			"1","2","","",	"","","", 	"Channel",""),
	array ("src_uid","",			"1","2","","",	"","","", 	"Channel UniqueID",""),
	array ("src_address","",		"1","2","","P",	"","","", 	"Channel Address",""),
	array ("src_vector","",			"1","2","","",	"","","", 	"Channel Direction",""),

	array ("reporter_id","",		"1","2","","f", "","","",	"Reporter ID",""),
	array ("reporter_contact_id","",	"1","2","","",	"","","",	"Reporter Contact ID",""),
	array ("reporter_fullname","",		"1","1","","",  "","","",	"Reporter Fullname",""),
	array ("reporter_phone","",		"1","2","","",  "","","",	"Reporter Phone",""), // todo: regex
	array ("reporter_email","",		"1","2","","",  "","","",	"Reporter Email",""),
	array ("reporter_phone2","",		"1","2","","",  "","","",	"Reporter Alternative Contact",""),
	array ("reporter_dob","",		"1","2","","",  "","","",	"Reporter Date of Birth",""),
	array ("reporter_age","",		"1","2","","",  "","","",	"Reporter Age",""),
	array ("reporter_age_group","",		"1","2","","",  "","","",	"Reporter Age Group",""),
	array ("reporter_sex","",		"1","2","","",  "","","",	"Reporter Gender",""),
	array ("reporter_national_id","",	"1","2","","",  "","","",	"Reporter National ID",""),
	array ("reporter_nationality","",	"1","2","","",  "","","",	"Reporter Nationality",""),
	array ("reporter_tribe","",		"1","2","","",  "","","",	"Reporter Tribe",""),
	array ("reporter_lang","",		"1","2","","",  "","","",	"Reporter Language",""),
	array ("reporter_landmark","",		"1","2","","",  "","","",	"Reporter Nearest Landmark",""),
	array ("reporter_location_0","",	"1","2","","",  "","","",	"Reporter Region",""),
	array ("reporter_location_1","",	"1","2","","",  "","","",	"Reporter District",""),
	array ("reporter_location_2","",	"1","2","","",  "","","",	"Reporter County",""),
	array ("reporter_location_3","",	"1","2","","",  "","","",	"Reporter Sub County",""),
	array ("reporter_location_4","",	"1","2","","",  "","","",	"Reporter Parish",""),
	array ("reporter_location_5","",	"1","2","","",  "","","",	"Reporter Village",""),
	
	array ("change_count","",		"4","1","","",  "au","COUNT(id)","", 	"Fields Affected",""), 		

	array ("yr","",				"4","2","","",   "case_activities","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(created_on)),'-01-01'))","",   "Year",":d:y:0: "), 
        array ("mn","",				"4","2","","",   "case_activities","UNIX_TIMESTAMP(CONCAT(YEAR(FROM_UNIXTIME(created_on)),'-',MONTH(FROM_UNIXTIME(created_on)),'-01'))","",   "Month",":d:my:0: "), 
        array ("wk","",				"4","2","","",   "case_activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on))) - (DAYOFWEEK(FROM_UNIXTIME(created_on))*86400)","",   "Week",":d:dmy:0: "), 
        array ("dt","",				"4","2","","",   "case_activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on)))","",   "Date",":d:dmy:0: "), 
	array ("hr","",				"4","2","","",   "case_activities","UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(created_on))) + (HOUR(FROM_UNIXTIME(created_on))*3600)","",   "Hour",":d:dmyh:0: "), 
        array ("h","",				"4","2","","",   "case_activities","HOUR(FROM_UNIXTIME(created_on))","",   "Hour",""), 
);


// ===================================================================================

$addr_dup = array ("addr","","dup","addr","addr", NULL,"id"); 
$otp_dup = array ("otp","","dup","addr","addr","expiry",":>now",NULL,"id"); // check if already pending
$otpv_dup = array ("otp","","dup","addr","addr","expiry",":>now", "otp","otp", NULL,"id", "addr_id", "addr"); // verify otp
$auth_dup = array ("users","","dup","usn","email",NULL, "id","contact_id","contact_fullname"); 
$contact_dup = array ("contacts","","dup","email","email",NULL, "id","fullname","role","phone","email"); 

$files_api = array
(
	array ("files","","file"),
);

$vfiles_api = array
(
	array ("vfiles","","file"),
);

$csv_api = array
(
	array ("csv","","file"),
);

$subcategories_api = array // todo: on update (202) propaget changes to childnodes tree!
(
        array ("subcategories","","dup","id","subcategory_id", NULL, "category_id:category_id"),
	array ("subcategories","","dup","name","name","category_id","category_id","id",":!=:subcategory_id:", NULL,"name:name"), // check duplicate name
	array ("categories","","dup","id","category_id",NULL,"id","name","fullname","fullname_id","level","root_id","root_name","category_id"), 
	array ("subcategories","",""),
	array ("subcategories","subcategories","agg4",  "id","subcategory_id", NULL,  "id","subcategory_id","category_id",":>: 0"), // agg only non-root
        array ("subcategories","subcategories","agg5",  "id","subcategory_id", NULL,  "id","subcategory_id","category_id",":>: 0"), // agg only non-root

);

$messages_api = array
(
        array ("pmessages","","dup","src","src","src_callid","src_callid", NULL, "id","src_callid:src_callid"), // link to first message
        array ("pmessages","",""),
        array ("messages","",""),
	array ("pmessages","pmessages","agg4", "id","pmsg_id",NULL,  "id","pmsg_id"), 	// update dt		
        array ("pmessages","messages","agg4", "id","pmsg_id", NULL,  "src_callid","src_callid"),
        array ("pmessages","messages","agg5", "id","pmsg_id", NULL,  "id","last_msg_id"),
);

$users_api = array
(
	array ("users","","dup","usn","usn","id",":!=:user_id: 0",NULL,"usn:usn"), // check duplicate usn
	array ("users","","dup","exten","exten","id",":!=:user_id: 0",NULL,"exten:exten"), // check duplicate exten
	array ("users","","dup","id","user_id",NULL,"contact_id"), // get contact_id for user
	array ("users","","params", "contact_fname","fname", "contact_phone","phone"), // used by try // avoid duplicating contact
	array ("users","","try"), // test if will succeed
	array ("contacts","",""), 
	array ("contacts","contacts","agg4", "id","contact_id",NULL, "id","contact_id"),
	array ("users","",""),
	array ("users","contacts","agg4", "id","user_id",NULL,  "id","contact_id"),
	array ("extens","","dup","user_id","user_id",NULL,"id"), // get exten_id (if exists) 
        array ("extens","",""),
       	array ("users","extens","agg4", "id","user_id",NULL,  "user_id","user_id"), // update user.exten
);

$contacts_api = array // todo: primary_contact_foreign_key (when someone calls with different number)
(
	array ("categories","","duf","id","age_group_id",NULL, "id:age_group_id", "fullname:age_group"),
	array ("categories","","duf","id","sex_id",NULL, "id:sex_id", "fullname:sex"),
	array ("categories","","duf","id","lang_id",NULL, "id:lang_id", "fullname:lang"),
	array ("categories","","duf","id","nationality_id",NULL, "id:nationality_id", "fullname:nationality"),
	array ("categories","","duf","id","national_id_type_id",NULL, "id:national_id_type_id", "fullname:national_id_type"),
	array ("categories","","duf","id","tribe_id",NULL, "id:tribe_id", "fullname:tribe"),
	array ("categories","","duf","id","location_id",NULL, "id:location_id", "fullname:location","fullname_id:location_fullname_id"),
	array ("contacts","","lvl","location_fullname_id","7","^",":", "location_","id_",""), // split loc levels
	array ("contacts","",""), // create | update contact
	array ("contacts","contacts","agg4",  "id","contact_id",NULL,  "id","contact_id"),
);

$contacts_disposition_api = array       // attach disposition to contact create/edit
(
        array ("contacts","","include"),
        array ("dispositions","","include"),
        array ("contacts","","params", "contact_disposition_id","contact_id"),
);

$contacts_dup_api = array
(
	array ("contacts","","dup","id","contact_id",NULL, 
"id","fullname", "fname", "lname",
"phone", "phone2", "email", "national_id",
"age", "dob", 
"age_group_id", "age_group", 
"sex_id", "sex", 
"national_id_type_id", "national_id_type", 
"nationality_id", "nationality", 
"is_refugee",
"tribe_id", "tribe", 
"lang_id", "lang", 
"location_id", "location",
"location_id_0", "location_id_1", "location_id_2", "location_id_3", "location_id_4", "location_id_5", "location_id_6", 
"location_0", "location_1", "location_2", "location_3", "location_4", "location_5", "location_6", 
"landmark")
);

$contacts_dup2_api = array
(
	array ("contacts","","dup","id","contact_id",NULL,  // map contact vars as reporter vars
"id:reporter_contact_id", "fullname:reporter_fullname", "fname:reporter_fname", "lname:reporter_lname",
"phone:reporter_phone", "phone2:reporter_phone2", "email:reporter_email", "national_id:reporter_national_id",
"age:reporter_age", "dob:reporter_dob", 
"age_group_id:reporter_age_group_id", "age_group:reporter_age_group", 
"sex_id:reporter_sex_id", "sex:reporter_sex", 
"national_id_type_id:reporter_national_id_type_id", "national_id_type:reporter_national_id_type", 
"nationality_id:reporter_nationality_id", "nationality:reporter_nationality", 
"is_refugee:reporter_is_refugee",
"tribe_id:reporter_tribe_id", "tribe:reporter_tribe", 
"lang_id:reporter_lang_id", "lang:reporter_lang", 
"location_id:reporter_location_id", "location:reporter_location",
"location_id_0:reporter_location_id_0", "location_id_1:reporter_location_id_1", "location_id_2:reporter_location_id_2", "location_id_3:reporter_location_id_3", "location_id_4:reporter_location_id_4", "location_id_5:reporter_location_id_5", "location_id_6:reporter_location_id_6", 
"location_0:reporter_location_0", "location_1:reporter_location_1", "location_2:reporter_location_2", "location_3:reporter_location_3", "location_4:reporter_location_4", "location_5:reporter_location_5", "location_6:reporter_location_6", 
"landmark:reporter_landmark")
);

$reporters_api = array				// update reporter
(
	array ("reporters","","aub"),
	array ("cases","","dup","id","case_id", NULL, "id"),
        // array ("contacts","","include"), 	// contact created via contacts^disposition
        array ("contacts","_dup","include"),
        array ("reporters","",""),
	array ("reporters","_dup","include"),
        array ("case_activities","","params", "activity_ref","reporter_id", "detail","contact_fullname"),
        array ("case_activities","","include")
);

$reporters_uuid_api = array 
(
	array ("cases","","dup","id","case_id", NULL, "id"),
	array ("contacts","","dup","id","contact_id", NULL, "id"),
	array ("contacts","","include"),	// create if does not exist
	array ("contacts","_dup","include"),
	array ("reporters","_uuid","")
);

$reporters_isclient_api = array 		// create|delete client from a reporter
(
	array ("reporters","","dup","id","reporter_id", NULL, "contact_id:contact_id","case_uuid:case_uuid"), // get contact_id
	array ("contacts","_dup","include"),
	array ("cases","","dup","id","case_id",NULL, "id", "uuid", "case_category:case_category", "priority", "status"), 
	
	array ("clients","","dup","contact_id","contact_id","case_uuid","case_uuid", NULL, "id"), // check if client_id already in case

	array ("clients","","aub"),
	array ("clients","",""),
	array ("reporters","clients","agg4", "id","reporter_id",NULL,  "contact_id","contact_id","case_uuid","case_uuid", "case_id_", ":!=: -9"), // set is_client flag
	
	array ("reporters","_dup","include"),
	array ("case_activities","","params", "activity_ref","reporter_id", "detail","contact_fullname", "reporter_isclient_id","reporter_id"),
	array ("case_activities","","include"),
);

$reporters_dup_api = array
(	
	array ("reporters","","dup","id","reporter_id", NULL, 
"id", "contact_id", 
"contact_fname:reporter_fname", "contact_lname:reporter_lname", "contact_fullname:reporter_fullname", 
"contact_phone:reporter_phone", "contact_phone2:reporter_phone2", "contact_email:reporter_email", "contact_national_id:reporter_national_id",
"contact_age:reporter_age", "contact_dob:reporter_dob", 
"contact_age_group_id:reporter_age_group_id", "contact_age_group:reporter_age_group",
"contact_sex_id:reporter_sex_id", "contact_sex:reporter_sex", 
"contact_lang_id:reporter_lang_id", "contact_lang:reporter_lang",
"contact_nationality_id:reporter_nationality_id", "contact_nationality:reporter_nationality",  
"contact_is_refugee:reporter_is_refugee",
"contact_tribe_id:reporter_tribe_id", "contact_tribe:reporter_tribe", 
"contact_location_id:reporter_location_id", "contact_location:reporter_location", 
"contact_location_id_0:reporter_location_id_0", "contact_location_id_1:reporter_location_id_1", "contact_location_id_2:reporter_location_id_2", "contact_location_id_3:reporter_location_id_3", "contact_location_id_4:reporter_location_id_4", "contact_location_id_5:reporter_location_id_5", "contact_location_id_6:reporter_location_id_6", 
"contact_location_0:reporter_location_0", "contact_location_1:reporter_location_1", "contact_location_2:reporter_location_2", "contact_location_3:reporter_location_3", "contact_location_4:reporter_location_4", "contact_location_5:reporter_location_5", "contact_location_6:reporter_location_6", 
"contact_landmark:reporter_landmark", "src_uid")
);

$clients_api = array 
(
	array ("clients","","dup","contact_id","contact_id","case_uuid","case_uuid",NULL,"id"), // check if client already exists
	array ("clients","","dup","id","client_id", NULL, "contact_id:contact_id:s"), 		// get contact_id
	array ("clients","","aub"),	
	array ("contacts","","include"),
 	array ("contacts","_dup","include"),
 	
	array ("categories","","dup","id","relationship_id",NULL, "id:relationship_id", "fullname:relationship"),
	array ("categories","","dup","id","health_id",NULL, "id:health_id", "fullname:health"),
	array ("categories","","dup","id","hiv_id",NULL, "id:hiv_id", "fullname:hiv"),
	array ("categories","","dup","id","disability_id",NULL, "id:disability_id", "fullname:disability"),
	array ("categories","","dup","id","school_level_id",NULL, "id:school_level_id", "fullname:school_level"),
	array ("categories","","dup","id","school_type_id",NULL, "id:school_type_id", "fullname:school_type"),
	array ("categories","","dup","id","marital_id",NULL, "id:marital_id", "fullname:marital"),
	array ("categories","","dup","id","spouse_profession_id",NULL, "id:spouse_profession_id", "fullname:spouse_profession"),
	array ("categories","","dup","id","guardian_marital_id",NULL, "id:guardian_marital_id", "fullname:guardian_marital"),
	array ("categories","","dup","id","household_id",NULL, "id:household_id", "fullname:household"),
	array ("categories","","dup","id","household_head_occupation_id",NULL, "id:household_head_occupation_id", "fullname:household_head_occupation"),
	array ("categories","","dup","id","not_in_school_id",NULL, "id:not_in_school_id", "fullname:not_in_school"),
	array ("cases","","dup","id","case_id",NULL, "id", "case_category:case_category", "priority", "status", "reporter_id:reporter_id"), // todo: use reporter_uuid instead to capture current reporter

	array ("clients","","params", "case_id_","case_id"),
	array ("clients","",""),
	array ("client_referals","","array"),
	
	array ("reporters","_dup","include"),	
	array ("case_activities","","params", "activity_ref","client_id","detail","contact_fullname"),	
	array ("case_activities","","include"),
);

$clients_del_api = array
(
	array ("clients","","aub"),	
	array ("clients","","params", "client_del_id","client_del_id", "client_id","client_del_id", "case_id_"," -9"),	
	array ("clients","",""),
	
	array ("clients","","dup", "id","client_id", NULL, "contact_id:contact_id", "case_uuid:case_uuid"),
	array ("reporters","","dup", "contact_id","contact_id", "uuid","case_uuid", NULL, "id"),	
	array ("reporters","clients","agg4", "id","reporter_id",NULL,  "contact_id","contact_id","case_uuid","case_uuid", "case_id_", ":!=: -9"), // set is_client flag
	
	array ("reporters","_dup","include"),	
	array ("case_activities","","params", "activity_ref","client_id", "detail","contact_fullname"),	
	array ("case_activities","","include"),
);

$client_referals_api = array 
(
	array ("categories","","dup","id","category_id",NULL, "id", "name", "fullname", "fullname_id"),
	array ("client_referals","","dup","category_id","category_id","client_id_","client_id", NULL, "id"), // check if exists
	array ("client_referals","","params", "client_id_","client_id"),
	array ("client_referals","","params", "client_id_","is_linked"),
	array ("client_referals","",""),
	array ("clients","client_referals","agg4",	"id","client_id",NULL,  "client_id_","client_id"),
);

$perpetrators_api = array 
(	
	array ("perpetrators","","dup","id","perpetrator_id",NULL, "contact_id:contact_id:s"), // get contact_id
	array ("contacts","","include"),	
 	array ("contacts","_dup","include"),
 	
	array ("categories","","dup","id","relationship_id",NULL, "id:relationship_id", "fullname:relationship"),
	array ("categories","","dup","id","shareshome_id",NULL, "id:shareshome_id", "fullname:shareshome"),
	array ("categories","","dup","id","marital_id",NULL, "id:marital_id", "fullname:marital"),
	array ("categories","","dup","id","health_id",NULL, "id:health_id", "fullname:health"),
	array ("categories","","dup","id","employment_id",NULL, "id:employment_id", "fullname:employment"),
	array ("categories","","dup","id","spouse_profession_id",NULL, "id:spouse_profession_id", "fullname:spouse_profession"),
	array ("cases","","dup", "id","case_id", NULL, "id","case_category:case_category", "priority", "status"),			
		
	array ("perpetrators","","aub"),	
	array ("perpetrators","","params", "case_id_","case_id"),
	array ("perpetrators","",""),
	
	array ("reporters","_dup","include"),	
	array ("case_activities","","params","activity_ref","perpetrator_id","detail","contact_fullname"),	
	array ("case_activities","","include")
);

$perpetrators_del_api = array
(
	array ("perpetrators","","aub"),	
	array ("perpetrators","","params", "perpetrator_del_id","perpetrator_del_id", "perpetrator_id","perpetrator_del_id", "case_id_"," -9"),	
	array ("perpetrators","",""),
	
	array ("reporters","_dup","include"),	// todo: use reporter_uuid_id
	array ("case_activities","","params","activity_ref","perpetrator_id","detail","contact_fullname"),
	array ("case_activities","","include"),
);

$attachments_api = array
(
	array ("files","","dup","id","file_id",NULL,"id","name","mime","size","uploadstatus","movestatus","channels","sample_rate","duration"),
	array ("cases","","dup","id","case_id",NULL,"id"),		
	array ("attachments","","params", "case_id_","case_id"),	
	array ("attachments","","aub"),	
	array ("attachments","",""),	

	array ("reporters","_dup","include"),
	array ("case_activities","","params", "activity_ref","attachment_id","detail","file_name"),	
	array ("case_activities","","include"),
);

$attachments_del_api = array
(
	array ("attachments","","dup","id","attachment_id", NULL, "file_id:file_id", "file_name:file_name", "case_id:case_id"), // needed for case_Activity
	array ("attachments","","params", "case_id_"," 0"),	
	array ("attachments","","aub"),
	array ("attachments","",""),

	array ("reporters","_dup","include"),	
	array ("case_activities","","params","activity_ref","attachment_id","detail","file_name"),	
	array ("case_activities","","include")
);

$services_api = array 
(
	array ("categories","","dup","id","category_id",NULL, "id", "name", "fullname", "fullname_id"),
	array ("services","","dup","category_id","category_id","case_id_","case_id", NULL, "id"), // check if exists
	array ("services","","params", "case_id_","case_id"),
	array ("services","","params", "case_id_","is_linked"),
	array ("services","",""),
	array ("cases","services","agg4", 	"id","case_id",NULL,  "case_id_","case_id"),
);

$referals_api = array 
(
	array ("categories","","dup","id","category_id",NULL, "id", "name", "fullname", "fullname_id"),
	array ("referals","","dup","category_id","category_id","case_id_","case_id", NULL, "id"), // check if exists
	array ("referals","","params", "case_id_","case_id"),
	array ("referals","","params", "case_id_","is_linked"),
	array ("referals","",""),
	array ("cases","referals","agg4",  	"id","case_id",NULL,  "case_id_","case_id")
);

$cases_api = array 
(
	array ("categories","","duf","id","case_category_id",NULL, "id:case_category_id", "fullname:case_category", "root_id:case_category_root_id", "fullname_id:case_category_fullname_id", "fullname"),
	array ("categories","","duf","id","justice_id",NULL, "id:justice_id", "fullname:justice"),
	array ("categories","","duf","id","assessment_id",NULL, "id:assessment_id", "fullname:assessment"),
	array ("categories","","duf","id","knowabout116_id",NULL, "id:knowabout116_id", "fullname:knowabout116"),
	array ("categories","","duf","id","disposition_id",NULL, "id:disposition_id", "name:disposition"),
	array ("users","","dup","id","escalated_to_id",NULL, "id:escalated_to_id", "usn:escalated_to", "role:escalated_to_role", "exten:escalated_to_exten", "id:assigned_to_id"),
	array ("users","","dup","id","escalated_by_id",NULL, "id:escalated_by_id", "usn:escalated_by", "role:escalated_by_role"),
	array ("users","","duf","id","assigned_to_id",NULL, "id:assigned_to_id", "usn:assigned_to", "role:assigned_to_role"),
	array ("cases","","lvl","case_category_fullname_id","5","^",":", "cat_","id_",""), // split cat levels

	array ("reporters","_uuid","object"),			// create reporter if object exist
	array ("cases","","params", "activity_","::case_id: case_new: case_edit", "reporter_id","reporter_uuid_id"),
	array ("reporters","_dup","include"),
	
        array ("cases","","aub"),
	array ("cases","",""), 
	array ("cases","cases","agg4",  "id","case_id",NULL,  "id","case_id"), 	// update dt
	array ("cases","","dup", "id","case_id", NULL, "id:case_id_","case_category:case_category", "priority", "status"),			
	array ("reporters","_case","include","1",""),		// update case_id during case create only
	array ("clients","_case","array","1",""),		// update case_id during case create only
	array ("perpetrators","_case","array","1",""), 		// update case_id during case create only
	array ("attachments","_case","array","1",""),		// update case_id during case create only
	array ("referals","","array"),
	array ("services","","array"),

	array ("case_activities","","params", "activity_ref","case_id", "detail","plan"),
	array ("case_activities","","include"),

	array ("dispositions","","params", "disposition_id","::disposition_id: ".$DISPOSITION_ID_COMPLETE.":disposition_id"),
        array ("dispositions","","dup","src","src","src_uid","src_uid","case_id","case_id",NULL,"id"), // get disposition_id (if exists)
	array ("dispositions","_include","include"),
);

$reporters_case_api = [  ["reporters","","","1"] ];
$clients_case_api = [ ["clients","","","1"] ];
$perpetrators_case_api = [  ["perpetrators","","","1"] ];
$attachments_case_api = [ ["attachments","","","1"] ];

$case_activities_api = array 
(
	array ("case_activities","",""),
	array ("case_activities","au","agg4",			"id","ca_id",NULL,  "aub_id","aub_id"), // change count
);

$activities_api = array
(
        array ("users","","dup","id","assigned_to_id",NULL, "id:assigned_to_id", "usn:assigned_to", "role:assigned_to_role"),
        array ("activities","","")
);

$dispositions_api = array
(
	array ("contacts","_dup","include"),
	array ("reporters","",""),
	array ("dispositions","","dup", "src","src", "src_uid","src_uid", "reporter_contact_id","contact_id", "case_id"," 0", "disposition_id",":!=: ".$DISPOSITION_ID_CONTACT_NEW, NULL,"id"), // get disposition_id (if exists)
	array ("dispositions","_include","include"),
);

$dispositions_unknown_api = array
(
	array ("categories","","dup","id","sex_id",NULL, "id:reporter_sex_id", "fullname:reporter_sex"),
	array ("categories","","dup","id","age_group_id",NULL, "id:reporter_age_group_id", "fullname:reporter_age_group"),
        array ("dispositions","","dup", "src","src", "src_uid","src_uid", "reporter_contact_id"," 0", "case_id"," 0", "disposition_id",":!=: ".$DISPOSITION_ID_CONTACT_NEW, NULL,"id"), // get disposition_id (if exists)
        array ("dispositions","_include","include"),
	array ("dispositions","","params", "dsp_unknown_id","dsp_id")
);

$dispositions_include_api = array
(
	array ("categories","","dup","id","disposition_id",NULL, "id:disposition_id", "name:disposition"),
	array ("reporters","_dup","include"),
        array ("dispositions","","params", "src_uid2","::src_uid2: nill:src_uid2", "src_uid_","src_uid", "src_uid2_","src_uid2", "is_active"," 1"),
        array ("dispositions","",""),
        array ("dispositions","dispositions","agg1",    "src","src","src_uid","src_uid", "case_id"," 0", NULL, "src","src","src_uid","src_uid", "case_id",":>: 0"), // unlink non-case (if with-case exists)
        array ("activities","dispositions","agg4",      "src","src", "src_uid","src_uid", NULL, "src","src","src_uid_","src_uid"),      // update activity (if exists)  
        array ("calls",	"dispositions","agg4",           "uniqueid","src_uid2",  NULL, "src"," call","src_uid2_","src_uid2"),            // update call (if exists)
	array ("pmessages","dispositions","agg4",	"src","src", "src_callid","src_callid",  NULL, "src","src", "src_callid","src_callid"), // update call (if exists)
);


// ===================================================================================

$categories_subs = 
[
["subcategories","","",	"category_id_","category_id"]
];

$categories_setup_subs = 
[
["subcategories","","",	"category_id","category_id"]
];

$calls_subs = 
[
["activities","","",	"chan_uniqueid","chan_uniqueid"],
["qas","","",		"chan_uniqueid","chan_uniqueid"],
];

$pmessages_subs = 
[
["messages","","200",	"src","src","src_callid","src_callid"],
];

$activities_subs = 
[
//["dispositions","","20",	"src_address","src_address"],
["messages","","100",           "src","src","src_callid","src_callid"]
];

$activities_case_subs = 
[
["cases","","",		"id","case_id"], // recursive!
];

$dispositions_subs =
[
["contacts","","",      "id","reporter_contact_id"],
["cases","_related","", "id","case_id"]
];

$contacts_disposition_subs =	
[
["subcategories","","100",      "category_id",(" ".$DISPOSITION_ROOT_ID)]
];

$reporters_uuid_subs = 
[
["cases","","",		"id","case_id"], // recursive!
];

$reporters_isclient_subs = 
[
["clients","","",	"id","client_id"]
];

$clients_del_subs = 
[
["reporters","","",	"id","reporter_id"],
];

$cases_subs = 
[
["reporters","","",	"id","reporter_id"],
["perpetrators","","",	"case_id_","case_id"],
["clients","","",	"case_id_","case_id"],
["attachments","","",	"case_id_","case_id"],
["case_activities","","","case_id","case_id"],
["dispositions","","",	"id","dsp_id"],
];

$case_activities_subs = 
[
["au","","",	"aub_id","aub_id"],
];

// ===================================================================================

$calls_join = 
[
"dispositions"=>["dispositions", "disposition", "disposition.src='call' && disposition.src_uid2_=chan.uniqueid"],
// "cases"=>["cases", "kase", "disposition.reporter_contact_id=kase.reporter_contact_id"],
];

$pmessages_join = 
[
"dispositions"=>["dispositions", "disposition", "disposition.src=pmsg.src && disposition.src_callid=pmsg.src_callid"],
// "cases"=>["cases", "kase", "disposition.reporter_contact_id=kase.reporter_contact_id"],
];

$contacts_join = 
[
"dispositions"=>["dispositions", "disposition", "contact.id=disposition.reporter_contact_id"],
"cases"=>["cases", "kase", "contact.id=kase.reporter_contact_id"],
];

$dispositions_join = 
[
// "cases"=>["cases", "kase", "disposition.reporter_contact_id=kase.reporter_contact_id"],
"cases"=>["cases", "kase", "disposition.case_id=kase.id"],
];

$cases_join = 
[
"clients"=>["clients", "client", "client.case_id_=kase.id"],
"perpetrators"=>["perpetrators", "perpetrator", "perpetrator.case_id_=kase.id"],
"services"=>["services", "service", "service.case_id_=kase.id"],
"referals"=>["referals", "referal", "referal.case_id_=kase.id"]
];

// ===================================================================================

$calls_csv = array ("uniqueid", "chan_ts", "vector", "trunk", "phone", "usr", "user_name", "wait_time_tot", "hold_time", "talk_time", "hangup_reason", "hangup_status_txt", "dispositions", "contacts");

$cases_csv=array(
"id",
"created_on",
"created_by",
"created_by_role",
"src",
//"case_category_root_id",
"cat_0",
"cat_1",
"cat_2",
"cat_3",
"cat_4",
"gbv_related",
"is_reporter_client",
"is_medical_exam_done",
"is_incidence_reported",
"is_hiv_tested",
"is_pep_given",
"is_art_given",
"is_ecp_given",
"is_counselling_given",
"police_ob_no",
"incidence_when",
"incidence_location",
"hiv_test_result",
"counseling_org",
"justice",
"assessment",
"escalated_to",
"priority",
"status",
"knowabout116",
"reporter_fullname",
"reporter_phone",
"reporter_phone2",
"reporter_dob",
"reporter_age",
"reporter_age_group",
"reporter_sex",
"reporter_national_id",
"reporter_nationality",
"reporter_tribe",
"reporter_lang",
"reporter_landmark",
"reporter_location_0",
"reporter_location_1",
"reporter_location_2",
"reporter_location_3",
"reporter_location_4",
"reporter_location_5",
"narrative",
"plan");

$clients_csv=array(
"contact_fullname",
"contact_phone",
"contact_phone2",
"contact_dob",
"contact_age",
"contact_age_group",
"contact_sex",
"contact_national_id",
"contact_nationality",
"contact_tribe",
"contact_lang",
"contact_landmark",
"contact_location_0",
"contact_location_1",
"contact_location_2",
"contact_location_3",
"contact_location_4",
"contact_location_5",
"relationship",
"relationship_comment",
"is_disabled",
"disability",
"health",
"hiv",
"special_services",
"in_school",
"school_type",
"school_level",
"school_attendance",
"school_name",
"school_address",
"not_in_school_reason",
"is_married",
"marital",
"spouse_profession",
"spouse_fullname",
"is_guardian_known",
"guardian_marital",
"guardian_fullname",
"guardian_national_id",
"household",
"household_adults",
"household_head_occupation",
"is_disabled_refered",
"is_disabled_referals",
"not_in_school");

$perpetrators_csv=array(
"contact_fullname",
"contact_phone",
"contact_phone2",
"contact_dob",
"contact_age",
"contact_age_group",
"contact_sex",
"contact_national_id",
"contact_nationality",
"contact_tribe",
"contact_lang",
"contact_landmark",
"contact_location_0",
"contact_location_1",
"contact_location_2",
"contact_location_3",
"contact_location_4",
"contact_location_5",
"relationship",
"shareshome",
"marital",
"health",
"employment",
"guardian_fullname",
"notes");

$services_csv=array("category_name");

$referals_csv=array("category_name");

// ===================================================================================

$hangupreason_enum = [ "peer"=>["peer","Agent"], "self"=>["self","Customer"] ];

$vector_enum = ["1"=>["1","Inbound"], "2"=>["2","Outbound"]];

$yesno_enum = 
[
"0"=>["0","No","No","Negative"], 
"1"=>["1","Yes","Yes","Positive"], 
"2"=>["2","Unknown","Unknown","Unknown"]
];

$charge_enum = ["0"=>["0","No"], "1"=>["1","Positive"], "2"=>["2","Unknown"]];

$role_enum = [
"1"=>["1","Counsellor"],
"2"=>["2","Supervisor"],
"3"=>["3","Case Manager"],
"4"=>["4","Case Worker"],
"5"=>["5","Partner"],
"99"=>["99","Administator"]
];

$case_type_enum = [
"87"=>["87","Abuse"],
"361944"=>["361944","Counseling"],
"362305"=>["362305","Information Inquiry"],
];
$case_status_enum = [""=>["","Unknown"], "0"=>["0","Unknown"], "1"=>["1","Ongoing"], "2"=>["2","Closed"]];

$case_priority_enum = [""=>["","Unknown"], "0"=>["0","Unknown"], "1"=>["1","Low"], "2"=>["2","Medium"], "3"=>["3","High"]];

$src_enum = 
[
"call"=>["call","Call","Phone Number","1"],
"walkin"=>["walkin","Walkin","Phone Number","1"],
"caseupd"=>["caseupd","Case Update","User",""],
"escalation"=>["escalation","Escalation","User",""],
"chat"=>["chat","Chat","Username",""],
"sms"=>["sms","SMS","Phone Number","1"],
"WENI"=>["WENI","Chat","Username",""],
"FACEBOOK"=>["FACEBOOK","Chat","Username",""],
"WHATSAPP"=>["WHATSAPP","Chat","Phone Number","1"],
"TWITTER"=>["TWITTER","Chat","Username",""],
"safepal"=>["safepal","Safepal","Username",""],
"webform"=>["webform","Web From","session",""],
"cmis"=>["cmis","CMIS","session",""],
];

?>
