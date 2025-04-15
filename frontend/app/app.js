
var APIPATH = "/helpline/api/";  

var UU = 
{
"login":{ 200:[["loadphone","ss"],["main","ss","vv"]], 401:[["login","user_","vv"]], 412:[["nb","errors","v","nb"]] },
"logout":{ 401:[["unloadphone","user_"],["login","user_","vv"]] },
"change_passwd":{ 202:[["change_passwd_vw","user_","vp"]], 412:[["nb","errors","v","nb"]] },
"reset_passwd":{ 202:[["nb","auth_nb","v","nb"]], 412:[["nb","errors","v","nb"]] },

"dash":{ 200:[["dash","dash"]] },
"dash_rpt_pie":{ 200:[["dash_rpt_pie","cases_rpt"]] },
"dash_rpt_line":{ 200:[["dash_rpt_line","cases_rpt"]] },
"dash_case_priority":{ 200:[["dash_case_priority","cases_rpt"]] },
"dash_calls_rpt_vw":{ 200:[["dash_calls_rpt_vw","calls_rpt"]] },
"dash_agent_name":{ 200:[["dash_agent_name","users"]] },

"today":{ 200:[["today","user_"]] },

"chan_agent_cid_name":{ 200:[["chan_agent_cid_name","users"]] },
"chan_add_ld":{ "203":[["chan_add_ld","action"]] },
"call_add_ld":{ "203":[["call_add_ld","action"]], 412:[["nb","errors","v","nb"]] },

"sup":{ "203":[["noop","action"]] },

"ati_end":{ "201":[["ati_ended","messages"]] }, // ati_ended
"nti_end":{ "201":[["nti_ended","messages"]] }, // ati_ended

"user_ed":{ 202:[["uvpfn","users","vp"]], 412:[["nb","errors","v","nb"]], 200:[["user_ed","users"]] },
"user_new":{ 201:[["uvpfn","users","vp"]], 412:[["nb","errors","v","nb"]] },
"user_vw_id":{ 200:[["user_vw_id","users"]] },
"user_la":{ 200:[["user_la","users_ctx"]] },
"user_lc":{ 200:[["user_lc","users_ctx"]] },
"user_lc_main":{ 200:[["user_lc_main","users_ctx"]] },
"user_ls":{ 200:[["user_ls","users_ctx"]] },
"user_list":{ 200:[["user_list","users_ctx"]] },
"user_main":{ 200:[["user_main","users_ctx"]] },
"users":{ 200:[["users","users_ctx"]] },

"schedules":{ 200:[["schedules","schedules_ctx"]] },

"category_ed":{ 200:[["category_ed","categories"]], 202:[["category_vw_id","subcategories","vp"]], 412:[["nb","errors","v","nb"]] },
"category_new":{ 201:[["category_r","subcategories","va"]], 412:[["nb","errors","v","nb"]] },
"category_vw_id":{ 200:[["category_vw_id","categories"]] },

"category_lc":{ 200:[["category_lc","subcategories_ctx"]] },

"category_lsh":{ 200:[["category_lsh","subcategories_ctx"]] },
"category_lsh_node":{ 200:[["category_lsh_node","categories"]] },
"category_lsh_main":{ 200:[["category_lsh_main","categories"]] },

"category_ls":{ 200:[["category_ls","subcategories_ctx"]] },

"category_rr":{ 200:[["category_rr","subcategories_ctx"]] },
"category_list":{ 200:[["category_list","subcategories_ctx"]] },
"category_main":{ 200:[["category_main","subcategories_ctx"]] },
"categories":{ 200:[["categories","subcategories_ctx"]] },

"subcategory_list":{ 200:[["subcategory_list","subcategories_ctx"]] },

"case_lc_main":{ 200:[["case_lc_main","subcategories_ctx"]] },
"case_location_lc_main":{ 200:[["case_location_lc_main","subcategories_ctx"]] },
"case_category_lc_main":{ 200:[["case_category_lc_main","subcategories_ctx"]] },

"vfile_vw_r":{ 404:[["vfile_not_found","errors"]] },

"contact_ed":{ 200:[["contact_ed","contacts"]], 202:[["contact_vw_id","contacts","vp"]], 412:[["nb","errors","v","nb"]] },
"contact_new":{ 201:[["contact_vw_id","contacts","vp"]], 412:[["nb","errors","v","nb"]] },
"contact_vw_id":{ 200:[["contact_vw_id","contacts"]] },
"contact_lc":{ 200:[["contact_lc","contacts_ctx"]] },
"contact_ls":{ 200:[["contact_ls","contacts_ctx"]] },
"contact_list":{ 200:[["contact_list","contacts_ctx"]] },
"contacts":{ 200:[["contacts","contacts_ctx"]] },

"qa_form":{ 201:[["uvpfn","calls","vp"]], 412:[["nb","errors","","nb"]] },
"qa_vw_id":{ 200:[["qa_vw_id","qas"]] },
"qa_list":{ 200:[["qa_list","qas_ctx"]] },
"qa_main":{ 200:[["qa_main","qas_ctx"]] },
"qas":{ 200:[["qas","qas_ctx"]], 201:[["qas","qas_ctx"]] },


"call_rpt_vw":{ 200:[["rpt_vw","calls_rpt"]] },
"call_dispositioned":{ 201:[["call_dispositioned","activities","vp"]], 202:[["call_dispositioned","activities","vp"]], 412:[["nb","errors","v","nb"]] },
"call_case":{ 200:[["call_case","cases_ctx"]] },
"call_vw_id":{ 200:[["call_vw_id","calls"]] },
"call_lst":{ 200:[["call_lst","calls_ctx"]] },
"call_list":{ 200:[["call_list","calls_ctx"]] },
"call_main":{ 200:[["call_main","calls_ctx"]] },
"calls":{ 200:[["calls","calls_ctx"]], 201:[["calls","calls_ctx"]] },

"pmessage_rpt_vw":{ 200:[["rpt_vw","pmessages_rpt"]] },
"pmessage_vw_id":{ 200:[["pmessage_vw_id","pmessages"]] },
"pmessage_list":{ 200:[["pmessage_list","pmessages_ctx"]] },
"pmessage_main":{ 200:[["pmessage_main","pmessages_ctx"]] },
"pmessages":{ 200:[["pmessages","pmessages_ctx"]] },

"activity_message_send":{ 201:[["activity_message_sended","messages","","sended"]] },
"activity_messages":{ 200:[["activity_messages_ufn","messages_ctx"]] },


"activity_call":{ 201:[["activity_call","activities"]], 202:[["activity_call","activities"]], 412:[["nb","errors","","nb"]] },

"activity_contact_list":{ 200:[["activity_contact_list","contacts_ctx"]] },

"activity_disposition_vwr":{ 200:[["activity_disposition_vwr","dispositions"]] },
"activity_disposition":{ 201:[["uvpfn","dispositions","vp"]], 412:[["nb","errors","v","nb"]], 200:[["activity_disposition","dispositions_ctx"]] },
"activity_disposition_new":{ 201:[["activity_disposition_new","cases_uuid"]], 412:[["nb","errors","v","nb"]] },


"activity_match_list":{ 200:[["activity_match_list","dispositions_ctx"]] },
"activity_match":{ 200:[["activity_match","dispositions_ctx"]] },

"activity_vw_id_messages_match":{ 200:[["activity_vw_id_messages_match","activities"]] },
"activity_vw_id_messages":{ 200:[["activity_vw_id_messages","activities"]] },
"activity_vw_id_match":{ 200:[["activity_vw_id_match","activities"]] },
"activity_vw_id":{ 200:[["activity_vw_id","activities"]] },
"activity_lst":{ 200:[["activity_lst","activities_ctx"]] },

// ---

"case_uuid_update":{ 201:[["case_update","cases"]], 412:[["nb","errors","v","nb"]] },
"case_uuid_edit":{ 201:[["case_ed","cases"]], 412:[["nb","errors","v","nb"]] },
"case_uuid_new":{ 201:[["case_new","r_"]], 412:[["nb","errors","v","nb"]] },

// ---

"reporter_duuid":{ 201:[["activity_disposition_new","r_"]], 	412:[["nb","errors"]] },
"reporter_fuuid":{ 201:[["case_vw_id","cases"]], 		412:[["reporter_not_selected","r_"]] },
"reporter_uuid": { 201:[["case_new","r_"]], 			412:[["reporter_not_selected","r_"]] },
"reporter_is_client":{ 202:[["reporter_isclient_ufn","reporters_isclient","va"]],  412:[["nb","errors","v","nb"]] },
"reporter_ed":{ 200:[["case_reporter_ed","reporters","vp"]], 202:[["uvpfn","reporters","vp"]], 412:[["nb","errors","v","nb"]] },
"reporter_new":{ 201:[["uvpfn","contacts","vp"]], 412:[["nb","errors","v","nb"]] },
"reporter_vw_id":{ 200:[["case_reporter_vw_id","reporters"]] },

"client_del":{ 202:[["case_client_del","clients_del","va"]], 412:[["nb","errors","v","nb"]] },
"client_ed":{ 202:[["uvpfn","clients","vp"]], 200:[["case_client_ed","clients","vp"]], 412:[["nb","errors","v","nb"]] },
"client_new":{ 201:[["uvpfn","clients","vp"]], 412:[["nb","errors","v","nb"]] },
"client_vw_id":{ 200:[["case_client_vw_id","clients"]] },

"perpetrator_del":{ 202:[["case_perpetrator_del","perpetrators_del","va"]], 412:[["nb","errors","v","nb"]] },
"perpetrator_ed":{ 202:[["uvpfn","perpetrators","vp"]], 200:[["case_perpetrator_ed","perpetrators","vp"]], 412:[["nb","errors","v","nb"]] },
"perpetrator_new":{ 201:[["uvpfn","perpetrators","vp"]], 412:[["nb","errors","v","nb"]] },
"perpetrator_vw_id":{ 200:[["case_perpetrator_vw_id","perpetrators"]] },

"case_attachment_del":{ 202:[["case_attachment_del","files","va"]], 412:[["nb","errors","","nb"]] },
"case_attachment":{ 201:[["case_attachment_","attachments"]] },
"case_attachment_new":{ 201:[["ufn_attach","files","va","nb"]], 412:[["nb","errors","","nb"]] },

"client_referal_del":{ 202:[["case_notif_del","client_referals"]], 412:[["nb","errors","v","nb"]] },
"referal_del":{ 202:[["case_notif_del","referals"]], 412:[["nb","errors","v","nb"]] },
"service_del":{ 202:[["case_notif_del","services"]], 412:[["nb","errors","v","nb"]] },

"case_contact_ed":{ 200:[["case_contact_ed","contacts"]], 202:[["uvpfn","contacts","vp"]], 412:[["nb","errors","v","nb"]] },
"case_contact_new":{ 201:[["uvpfn","contacts_disposition","vp"]], 412:[["nb","errors","v","nb"]] },

"case_rpt_vw":{ 200:[["rpt_vw","cases_rpt"]] },
"case_update":{ 202:[["uvpfn","cases","vp"]], 412:[["nb","errors","v","nb"]], 200:[["case_update","cases"]] },
"case_ed":{ 202:[["activity_case_ufn","cases","vfvw"]], 412:[["nb","errors","v","nb"]], 200:[["case_ed","cases"]] },
"case_new":{ 200:[["case_new","cases"]], 201:[["activity_case_ufn","cases","vfvw"]], 202:[["activity_case_ufn","cases","vfvw"]], 412:[["nb","errors","v","nb"]] },
"case_vw_id":{ 200:[["case_vw_id","cases"]] },
"case_vw":{ 200:[["case_vw","cases"]] },
"case_list":{ 200:[["case_list","cases_ctx"]] },
"case_main":{ 200:[["case_main","cases_ctx"]] },
"cases":{ 200:[["cases","cases_ctx"]] },

"case_history_vw_id":{ 200:[["case_history_vw_id","case_activities"]] },
"case_history":{ 200:[["case_history","case_activities_ctx"]] },

};

re["peers"] = {};
re["channels"] = {};
re["categories_age_group"] = [];
re["callfile_"] = [["","","","","","","","","","", "","","","","","","","","","", "/helpline/api/calls/","?file=wav"]];
re["vfile_"] = [["","","","","","","","","","", "","","","","","","","","","", "/helpline/api/vfiles/","?file=wav"]];
re["qa_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["activity_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["task_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["call_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["category_"] = [["","","","","","","","","","","","","","","","","","",""]];
re["workinghour_"] = [["","","","","","","","28800","61200","","","","","","","","",""]];
re["campaign_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["shift_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["voicefile_"] = [["","","","","","","","","","","","","","","","","","","","",""]];
re["voicemap_"] = [["","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["voiceprompt_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["user_"] = [["","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["chan_"] = [["","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","" ]];
re["reporter_"] = [["","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","", "","","","","","","","","","0",  "","","","",""]];
re["r_"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","", "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",
"","","","","","","","","","","","","","","","","","","","","","","","","", "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","", "","","","","","","","","","","","","","","","","","","","","","","", "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];

re["auth"] = [["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]];
re["contacts_k"] = {};
re["categories_k"] = {};
re["activities_k"] = {};
re["actions_k"] = {};
re["cases_k"] = {};
re["reporters_k"] = {};
re["clients_k"] = {};
re["perpetrators_k"] = {};
re["messages_k"] = {};
re["qas_k"] = {};
re["dispositions_k"] = {};

rk["dist"] = ["-","h","dt","wk","mn","yr"];
re["dist"] = 
{
"":["","None"],
"-":["-","Pie Chart"],
"h":["h","Hourly"],
"dt":["dt","Day"],
"wk":["wk","Week"],
"mn":["mn","Month"],
"yr":["yr","Year"],
};
rk["dash_call_dist"] = ["hour","-"];
re["dash_call_dist"] = re["dist"];

rk["sla"] = ["120+","120","100","80","60","40","20","0"]; 
re["sla"] = 
{
"120+":["120+","140+",""],
"120":["120","120-139",""],
"100":["100","100-119",""],
"80":["80","80-99",""],
"60":["60","60-79",""],
"40":["40","40-59",""],
"20":["20","20-39",""],
"0":["0","0-19",""],
};

rk["sla_wait"] = ["120+","120","100","80","60","40","20","0"]; 
re["sla_wait"] = re["sla"];

rk["hangup_reason"] = ["phone","usr","ivr","net"];
re["hangup_reason"] = 
{
"":["","",""],
"phone":["phone","Customer"],
"usr":["usr","Extension"],
"ivr":["ivr","IVR"],
"net":["net","Network"],
};

rk["hangup_status"] = ["answered","abandoned","dump","missed","ivr","noanswer","busy","networkerror","voicemail","xfer_consult","xfer_noanswer","xfer_offline","xfer_ok"];
re["hangup_status"] = 
{
"":["","","","",""],
"answered":["answered","Answered","Answered","x y03 gg cw","","#4eb151"],
"abandoned":["abandoned","Abandoned","Abandoned","x y03 go cw","","#ffa500"],
"dump":["dump","AgentDump","Dump","x y03 gr cw","","#B22222"],
"ivr":["ivr","IVR","","g","","#1E90FF"],
"missed":["missed","Missed","Missed","x y03 go cw","","#DC143C"],
"no-answer":["no-answer","Flash","No Answer","x y03 go cw","","#FFA07A"],
"noanswer":["no-answer","Flash","No Answer","x y03 go cw","","#FFA07A"],
"busy":["busy","Busy","Busy","x y03 go cw","","#FF6347"],
"networkerror":["network-error","Network Error","Network Error","x y03 gwd cb","","#FF00FF"],
"voicemail":["voicemail","Voicemail","Voicemail","x y03 gr cw","","#90EE90"], 
"xfer_consult":["xfer_consult","Consult","Consult","x y03 gg cw","","#20B2AA"],
"xfer_noanswer":["xfer_noanswer","Transfer No Answer","Transfer No Answer","x y03 go cw","","#20B2AA"],
"xfer_offline":["xfer_offline","Transfer Unavailable","Transfer Unavailable","x y03 go cw","","#20B2AA"],
"xfer_ok":["xfer_ok","Transferred","Transfer Successful","x y03 gg cw","","#20B2AA"],
"SCHED":["SCHED","Sched","Scheduled","x y03 gg cw","","#20B2AA"],
"Reattempt":["Reattempt","Reattempt","Reattempt","x y03 gg cw","","#20B2AA"],
};


rk["lead_status"] = ["answered","busy","dump","no-answer","network-error","voicemail","SCHED","Reattempt"];
re["lead_status"] = re["hangup_status"]; 


//rk["vector"] = ["1","2"];
//re["vector"] = 
//{
//"":["","","","","","","","","","","","","","","","","","","","",""],
//"0":["0","","","","","","","","","","","","","","","","","","","",""],
//"1":["1","Inbound","&#8702","From",  "Outbound","&#8701","To", "g","Outbound Call",,"c w80","c xx y bd8 gg cw","x08 y s cd"],
//"2":["2","Outbound","&#8701","To",  "Inbound","&#8702","From", "","Inbound Call",,"d w80","d xx y bd8 go_ cb","x08 y tr s cd"],
//};

rk["vector"] = ["1","2"];
re["vector"] =
{
"":["","","","","","","","","","","","","","","","","","","","",""],
"0":["0","","","","","","","","","","","","","","","","","","","","","","","",""],
"1":["1","Inbound","&#8702","From",  "Outbound","&#8701","To", "g","Outbound Call",,"c w50","c xx y08 bd8 go cw","y s cd", "c x","g"],
"2":["2","Outbound","&#8701","To",  "Inbound","&#8702","From", "","Inbound Call",,"d w50","d xx y08 bd8 gg cw","y s cd tr","d x",""],
};         



rk["user_role"] = ["1","2","3","4","5","6","99"];
re["user_role"] = 
{
"":["","","","",""],
"0":["","","","",""],
"1":["1","Counsellor","counsellor","2",""],
"2":["2","Supervisor","supervisor","3","1"],
"3":["3","Case Manager","casemanager","4",""],
"4":["4","Case Worker","caseworker","0",""],
"5":["5","Partner","partner","0",""],
"6":["6","Media Account","media","2",""],
"99":["99","Administator","admin","99","1"],
};

re["onbreak"] = 
{
"":["","Offline"],
"coffee":["coffee","Coffee Break"],
"lunch":["lunch","Lunch Break"],
"FX":["FX","On Break"],
};

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

rk["campaign"] = ["1","2"];  // match spefic date first then 
re["campaign"] = 
{
"":["","", "noop", "noop", "noop-noop-ve-type", "noop","", ""],
"1":["1","Inbound", "campaign_vw_inbound", "campaign_ed_inbound", "campaign_ed_inbound-campaign_-ve-type", "campaign_vw_id_menu_inbound","campaign_vw_tabs_inbound", "Inbound Campaign"],
"2":["2","Outbound", "campaign_vw_outbound", "campaign_ed_outbound", "campaign_ed_outbound-campaign_-ve-type", "campaign_vw_id_menu_outbound","campaign_vw_tabs_outbound", "Outbound Campaign"],
};


rk["workinghour_priority"] = ["","0","1","2","3","4","5"];  
re["workinghour_priority"] = 
{
"":["","",""],
"0":["0","Disabled","", "--"],
"1":["1","Out of Office","","OO"],
"2":["2","Working Hours","", "WH"],
"3":["3","Reattempt Hours","","RH"],
"4":["4","Holiday","","HD"],
"5":["5","Event","","EV"],
};

rk["workinghour_priority_inbound"] = ["2","0"];  
re["workinghour_priority_inbound"] = re["workinghour_priority"];

rk["workinghour_priority_outbound"] = ["2","3","0"];  
re["workinghour_priority_outbound"] = re["workinghour_priority"];

rk["ooohour_priority"] = ["1","4","5","0"];  
re["ooohour_priority"] = re["workinghour_priority"];


re["contact_fields"] = 
{
"fname":["fname","First Name"],
"lname":["lname","Last Name"],
"phone":["phone","Phone"],
};

re["dialstatus"] = 
{
"ANSWER":["ANSWER","Answered the call"],
"BUSY":["BUSY","is Busy"],
"NOANSWER":["NOANSWER","did Not-Answer"],
"CANCEL":["CANCEL","is Unavailable"],
"CHANUNAVAIL":["CHANUNAVAIL","is Unavailable"],
"DONTCALL":["DONTCALL","is Unavailable"],
"DONTCALL":["DONTCALL","is Unavailable"],
"INVALIDARGS":["INVALIDARGS","is Unavailable"]
};



rk["case_priority"] = ["1","2","3","0"];
re["case_priority"] =
{
"":["","Blank","","","","#ffffff"],
"0":["0","None","","","","#ffffff"],
"1":["1","Low","Low Priority","","","#4eb151"],
"2":["2","Medium","Medium Priority","","","#ffa500"],
"3":["3","High","High Priority","","","#ff0000"],
};


rk["case_status"] = ["1","2","3","0"];
re["case_status"] =
{
"":["","Blank","","","","#ffffff"],
"0":["0","None","","","","#ffffff"],
"1":["1","Ongoing","Ongoing","","","#ffa500"],
"2":["2","Closed","Closed","","","#4eb151"],
"3":["3","Escalated","Escalated to","","","#ff0000"],
};


rk["case_priority_form"] = ["1","2","3"];
re["case_priority_form"] = re["case_priority"];

rk["case_status_form"] = ["1","2"];
re["case_status_form"] = re["case_status"];


//
//rk["case_src"] = ["walkin","call","sms","email","safepal","WHATSAPP","FACEBOOK","TWITTER"];
//re["case_src"] = 
//{
//"":["","","","edit","","","","",""],
//"walkin":["walkin","Walkin","Walkin Activity","walkin",		"activity_btns","activity_match","activities"],
//"call":["call","Call","Call Activity","call",			"cti_btns","activity_match","activities"],
//"sms":["sms","SMS","SMS Activity","sms",			"ati_btns","activity_messages_main","activities"],
//"email":["email","Email","Email Activity","email",		"ati_btns","activity_messages_main","activities"],
//"safepal":["safepal","SafePal","Safepal Activity","chat",	"ati_btns","activity_messages_main","activities"],
//"whatsup":["whatsup","Whatsup","Whatup Activity","chat",	"ati_btns","activity_messages_main","activities"],
//"facebook":["facebook","Facebook","Facebook Activity","chat",	"ati_btns","activity_messages_main","activities"],
//"twitter":["twitter","Twitter","Twitter Activity","chat",	"ati_btns","activity_messages_main","activities"],
//"chat":["chat","Chat","Chat Activity","chat",			"ati_btns","activity_messages_main","activities"],
//"escalation":["escalation","escalation","Escalation","notify",	"nti_btns","activity_case_notify","activities^case"],
//"WENI":["WENI","WENI","Chat Activity","chat",                   "ati_btns","activity_messages_main","activities"],
//"FACEBOOK":["FACEBOOK","FACEBOOK","Chat Activity","chat",                   "ati_btns","activity_messages_main","activities"],
//"WHATSAPP":["WHATSAPP","WHATSAPP","Chat Activity","chat",                   "ati_btns","activity_messages_main","activities"],
//"TWITTER":["TWITTER","TWITTER","Chat Activity","chat",                   "ati_btns","activity_messages_main","activities"],


rk["case_src"] = ["walkin","call","sms","email","safepal","chat","WHATSAPP","FACEBOOK","TWITTER","WENI"];
re["case_src"] = 
{                               
//"":["","",""],          
"":["edit","edit","",                               "g","", "g","edit","Edit Activity",                             "noop","activity_vw_id_match", "Edit", "", ""],

"all":["all","Total",":k:case_source:total:1",          "g","", "micon hh co","cases","All Cases",                      "noop","noop","","", ""],
"social":["social","Social Media",":k:case_source:socialmedia:1", "g","", "micon cbl hh","share","Social Media",        "noop","noop","","", ""],
"edit":["edit","edit","",                               "g","", "g","edit","Edit Activity",                             "noop","activity_vw_id_match", "Edit", "", ""],
"walkin":["walkin","Walkin",":k:case_source:walkin:1",  "g","", "micon cg hh","directions_walk","Walkin Activity",      "activity_btns","activity_vw_id_match","Walkin", "reporter_phone", ""],
"call":["call","Call",":k:case_source:call:1",          "","/helpline/images/bxs-phone-call.png","g","call","Call Activity","cti_btns","activity_vw_id_match","Call", 
"reporter_phone", ""],
"sms":["sms","SMS",":k:case_source:sms:1",              "","/helpline/images/sms.png","g","sms","SMS Activity",            "ati_btns","activity_vw_id_messages","SMS Chat", "reporter_phone", ""],
"email":["email","Email",":k:case_source:email:1",      "","/helpline/images/envelope-fill.png","g","chat","Email Activity","ati_btns","activity_vw_id_messages","Email", "reporter_email", ""],
"safepal":["safepal","SafePal","",                      "","/helpline/images/safepal_ico.png","g","chat","Safepal Activity","ati_btns","activity_vw_id_messages","Safepal", "reporter_phone", "safepal"],
"whatsup":["whatsup","Whatsup","",                      "","/helpline/images/watsap_ico.png","g","chat","Whatup Activity", "ati_btns","activity_vw_id_messages","Whatsapp Chat", "reporter_phone", ""],
"facebook":["facebook","Facebook","",                   "","/helpline/images/fb_ico.png","g","chat","Facebook Activity",   "ati_btns","activity_vw_id_messages","Facebook Posts", "reporter_email", ""],
"twitter":["twitter","Twitter","",                      "","/helpline/images/twitter_ico.png","g","chat","Twitter Activity","ati_btns","activity_vw_id_messages","Twitter Posts", "reporter_email", ""],
"chat":["chat","Chat","",                               "","/helpline/images/chat.png","g","chat","Chat Activity",         "ati_btns","activity_vw_id_messages","Web Chat", "reporter_phone", "safepal"],
"escalation":["escalation","Escalation","",		"","","","","",							   "nti_btns","activity_vw_id_notify","activities^case", "reporter_phone", ""],
"WENI":["WENI","WENI","",                      		"","/helpline/images/watsap_ico.png","g","chat","WENI Activity", "ati_btns","activity_vw_id_messages","Weni Chat", "reporter_phone", ""], 
"WHATSAPP":["WHATSAPP","WHATSAPP","",                   "","/helpline/images/watsap_ico.png","g","chat","Whatsup Activity", "ati_btns","activity_vw_id_messages","Whatsapp Chat", "reporter_phone", ""],
"FACEBOOK":["FACEBOOK","FACEBOOK","",                   "","/helpline/images/watsap_ico.png","g","chat","Facebook Activity", "ati_btns","activity_vw_id_messages","Facebook Chat", "reporter_email", ""], 
"TWITTER":["TWITTER","TWITTER","",                      "","/helpline/images/watsap_ico.png","g","chat","Twitter Activity", "ati_btns","activity_vw_id_messages","Twitter Chat", "reporter_email", ""], 
};

 
rk["safepal"] = ["id", "incident_report_id", "survivor_name", "survivor_gender", "survivor_contact_phone_number", "survivor_contact_email", "survivor_age", "unique_case_number", "incident_location", "incident_date_and_time", "incident_type", "incident_descriptio", "incident_reported_by", "number_of_perpetrators", "perpetrator_name", "perpetrator_gender", "perpetrator_estimated_age", "perpetrator_relationship", "perpetrator_location", "date_of_interview_with_cso", "chl_status", "chl_case_id", "chl_time", "chl_user_id"]; // safepal msg object schema
re["safepal"] = 
{
"id": 			["id","ID"], 
"incident_report_id": 	["incident_report_id","Reporter ID"], 
"survivor_name": 	["survivor_name","Survivor Name"], 
"survivor_gender": 	["survivor_gender","Survivor Gender"], 
"survivor_contact_phone_number": ["survivor_contact_phone_number","Survivor Phone"], 
"survivor_contact_email": ["survivor_contact_email","Survivor Email"], 
"survivor_age": 	["survivor_age","Survivor Age"], 
"unique_case_number": 	["unique_case_number","Unique Case Number"], 
"incident_location": 	["incident_location","Incident Location"], 
"incident_date_and_time": ["incident_date_and_time","Incident DateTime"], 
"incident_type": 	["incident_type","Incident Type"],
"incident_descriptio": 	["incident_descriptio","Incident Description"],
"incident_reported_by": ["incident_reported_by","Incident Reported By"],
"number_of_perpetrators": ["number_of_perpetrators","Nuber of Perpetrators"],
"perpetrator_name": 	["perpetrator_name","Perpetrator Name"],
"perpetrator_gender": 	["perpetrator_gender","Perpetrator Gender"],
"perpetrator_estimated_age": ["perpetrator_estimated_age","Perpetrator Estmated Age"],
"perpetrator_relationship": ["perpetrator_relationship","Perpetrator Location"],
"perpetrator_location": ["perpetrator_location","Perpetrator Location"],
"date_of_interview_with_cso": ["date_of_interview_with_cso","Date of Interview with CSO"],
"chl_status": 		["chl_status","CHL Status"],
"chl_case_id": 		["chl_case_id","CHL Case ID"],
"chl_time": 		["chl_time","CHL Tie"],
"chl_user_id": 		["chl_user_id","CHL User"],
};


rk["dash_src"] = ["all","call","sms","social","email","walkin"];
re["dash_src"] = 
{
"all":["all","Total","go", "/helpline/images/case.png", ":k:case_source:total:1"],
"call":["call","Calls","", "/helpline/images/bxs-phone-call.png", ":k:case_source:call:1"],
"sms":["sms","SMS","", "/helpline/images/sms.png", ":k:case_source:sms:1"],
"social":["social","Social Media", "", "/helpline/images/chat.png", ":k:case_source:socialmedia:1"],
"email":["email","Email", "", "/helpline/images/envelope-fill.png", ":k:case_source:email:1"],
"walkin":["walkin","Walkin", "gg", "/helpline/images/walkin.png", ":k:case_source:walkin:1"],
};

re["disposition"] = 
{
"":["","",""],
"":["","",""],
"appreciation":["appreciation","Appreciation",""],
"abusive":["abusive","Abusive Call",""],
"adult_related":["adult_related","Adult Related",""],
"counsellor":["counsellor","Counsellor Request",""],
"complaint":["complaint","Complaint",""],
"dropped":["dropped","Dropped",""],
"feedback":["feedback","Feedback",""],
"greeting":["greeting","Greeting",""],
"inquiry":["inquiry","Inquiry",""],
"insuff":["insuff","Insufficient Information",""],
"mistake":["mistake","Mistake",""],
"prank":["prank","Prank",""],
"silent":["silent","Silent Call",""],
"telkom":["telkom","Telkom Support",""],
"testing":["testing","Testing Line",""],
"complete":["complete","Call Completed",""],
};

rk["incomplete_call"] = ["appreciation","abusive","adult_related","counsellor","complaint","dropped","feedback","greeting","inquiry","insuff","mistake","prank","silent","telkom","testing"];
re["incomplete_call"] = re["disposition"];

re["activity_status"] = 
{
"0-1-":["","Network Error"],
"1-1-":["","Busy"],
"2-1-":["","No Answer"],
"3-1-":["","Answered"],
"4-1-":["","Answered"],
"5-1-":["","Answered"],
"6-1-":["","Answered"],
"7-1-":["","Answered"],
"8-1-":["","Answered"],
"0-2-":["","Error"],
"1-2-":["","Busy"],
"2-2-":["","Missed"],
"3-2-":["","Answered"],
"4-2-":["","Answered"],
"5-2-":["","Answered"],
"6-2-":["","Answered"],
"7-2-":["","Answered"],
"8-2-":["","Answered"],
"0-2-0":["","Error"],
"1-2-0":["","Busy"],
"2-2-0":["","Missed"],
"3-2-0":["","Answered"],
"4-2-0":["","Answered"],
"5-2-0":["","Answered"],
"6-2-0":["","Answered"],
"7-2-0":["","Answered"],
"8-2-0":["","Answered"],
"0-2-1":["","Error"],
"1-2-1":["","Busy"],
"2-2-1":["","Missed"],
"3-2-1":["","Answered"],
"4-2-1":["","Answered"],
"5-2-1":["","Answered"],
"6-2-1":["","Answered"],
"7-2-1":["","Answered"],
"8-2-1":["","Answered"],

};

rk["qa_done"] = ["-1","0","1"];
re["qa_done"] = 
{
"":["",""],
"-1":["-1","N/A"],
"0":["0","No"],
"1":["1","Yes"],
};

rk["dash_period"] = ["today","this_week","this_month","last_3_month","last_6_month","last_9_month","this_year","all"];
re["dash_period"] =
{
"today":["today","Today"],
"this_week":["this_week","This Week"],
"this_month":["this_month","This Month"],
"last_3_month":["last_3_month","Last 3 Months"],
"last_6_month":["last_6_month","Last 6 Months"],
"last_9_month":["last_9_month","Last 9 Months"],
"this_year":["this_year","This Year"],
"all":["all","All"],
};

rk["dash_gbv"] = ["both","vac","gbv"];
re["dash_gbv"] = 
{
"both":["both","Both VAC & GBV"],
"vac":["vac","VAC Only"],
"gbv":["gbv","GBV Only"]
};

re["case_activity"] =
{
"1":["1","Case Created"],
"2":["2","Case Update"],
"3":["3","Case Edit"],
"4":["4","Case Change Type"],
"6":["6","Client Added"],
"7":["7","Perpetrator Added"],
"8":["8","Attachment Added"],
"9":["9","Reporter Updated"],
"10":["10","Client Updated"],
"11":["11","Perpetrator Updated"],
"12":["12","Attachment Updated"],
"13":["13","Client Deleted"],
"14":["14","Perpetrator Deleted"],
"15":["15","Attachment Deleted"]	
};


re["reporter_is_client"] = 
{
"":["","No","Is Not","","","",""],
"0":["0","No","Is Not","","","",""],
"1":["1","Yes","Is","xx y gwd bd8","Is Client","Reporter","1"],
};


re["metrics"] = 
{
"case_count":["case_count", "Case Count","Case Count","",			"cases","","case_count", 		"","",,"", "0","","",""], 
"pmessage_count":["pmessage_count", "Message Session Count","Message Session Count","",	 "pmessages","","pmessages_count", 	"","",,"", "0","","",""], 
"call_count":["call_count", "Call Count","Call Count","",			"calls","","call_count", 		"","",,"", "0","","",""], 
};

re["loclev"] = 
{
"":["","",""],
"0":["0","",""],
"1":["1","Region",""],
"2":["2","District",""],
"3":["3","County",""],
"4":["4","SubCounty",""],
"5":["5","Parish",""],
"6":["6","Village",""],
"7":["7","Constitunecy",""],
};

// -------------------------------------------------------------------

te["unloadphone"] = { ufn:["unloadphone"] };

te["loadphone"] = { ufn:["loadphone"] };

// -------------------------------------------------------------------

te["vfile_not_found"] = { s:["xx y gp cr bd8","Recording Not Found"] };

te["vp_apply"] = { div:["x25 t b15"], c: // 
[
	{ div:["d l15"], c:[ { ac:["ag btn w06",null,"_uvpf","x y04 w05 gb cw tc","Apply"] }, { s:["y07 bd b savl","..."] } ] },
	{ div:["d","va"], ac:["ay","","_uvp","x y03 w05 ba tc cd","Cancel"] },
	{ div:["e"] }
]};

te["vp_sav"] = { c:
[
	{ div:["d l15"], c:
	[ 
		{ ac:["ag btn",null,null,"w10 y gb cw tc",null] }, 
		{ s:["y b savl",null] } 
	]},
	{ div:["d","va"], ac:["ay",null,null,"w09 y04 ba tc cd",""], c:
	[ 
		{ s:["",null] },
		{ p:["g","o"], arg:["",".id","%0"] } 
	]},
	{ div:["e"] }
]};

// -----------------------------------------------------------------

te["tabi"] = { div:[null], c: 	
[
	{ input:["g","",null,null,"radio",null] },
	{ li:["y ba cb tc tabi",null], ev:[null], c:
	[
		{ s:["",null] },
		{ arg:["",".id","%0"] }
	]},
]};

te["tab"] = { c:
[
	{ arg:["","",""] }, // ts
	{ input:["g","",null,null,"radio",null] },
	{ li:[null,null], ev:["_tab"], c:
	[
		//{ div:["c"], c:[ { img:["","",null,"20"] } ] },
		{ s:[null,null] },
		{ div:["e"] } // , arg:["_c","","30"] }
	]},
]};

// --------------------------------------------------------------------

te["change_passwd_vw"] = { div:["w45 ma bd sh__ gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["xx y"], c:
	[
		{ s:["c xx yy b cg","Password Changed Successful"] },
		{ ac:["d w03 ay y","","_uvp","x y tc h2 cb bd","&Cross;"] },
		{ div:["e"] }
	]},
]};

te["change_passwd"] = { div:["w50 ma bd sh__ gw_"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b","Change Password"] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},

	{ div:["","ve"], c:
	[
		{ div:["x25"], c:[ { p:["c w40","nb"], u:["nb","users_nb"] }, { div:["e"] } ] },
		{ p:["x25","o"], c:
		[
			{ div:["t15"], c:
			[ 
				{ s:["c w15 y","Current Password"] }, { passwd:["d w25 gw_ ba","w25 x y","","pass0",""] }, { div:["e"] } 
			]},
			{ div:["t15"], c:
			[
				{ s:["c w15 y","New Password"] }, { passwd:["d w25 gw_ ba","w25 x y","","pass1",""] }, { div:["e"] }
			]},
			{ div:["t15"], c:
			[
				{ s:["c w15 y","Confirm Password"] }, { passwd:["d w25 gw_ ba","w25 x y","","pass2",""] }, { div:["e"] }
			]},
		]},
		{ div:["x25 t30 b20"], vp_sav:["change_passwd-changeAuth","_postj","Change Password","Changing...","myprofile-user_","_vp","Cancel"] }
	]}
]};

te["myprofile"] = { div:["w70 ma bd sh__ gw","vddvw"], ev:["_undd"], c:
[

	{ div:["x15 y15"], c:
	[
		{ s:["x yy b cb h2","My Profile"] },
		{ ac:["","change_passwd-user_","_vp","x y",""], c:
		[
			{ s:["","Change Password"] },
			{ div:[] }
		]},
	]},
	{ div:["x15 yy"], c:
	[
		{ div:["c xx yy w40 gw mb mr10 g"], c:
		[
			{ s:["x yy","Active Campaigns"] },
		]},
		{ div:["c xx yy w40 gw mb mr10"], c:
		[
			{ s:["x y","Availability"] },
			{ s:["x y","Answered Calls"] },
			{ s:["x y","Missed Calls"] },
			{ s:["x y","Average Talk Time"] },
			{ s:["x y","Max Talk Time"] },
			{ s:["x y","Average Hold Time"] },
			{ s:["x y","Max Hold Time"] },
			{ s:["x y","Total Break Time Today"] },
			{ s:["x y","Average "] },
		]},
		{ div:["e"] }
	]},
	{ div:["x15 yy g"], c:
	[
		{ s:["x yy c b","Availability History"] }

	]}
	

]};

// -------------------------------------------------------------------

te["settings"] = { div:["h80 go abs","vb"], c: 
[

]};

// -------------------------------------------------------------------

te["dash_agent_name"] = { s:["",":v:users:usn"] };

te["dash_agent"] = { p:["bb_ bl_ br_",":v:users:exten"], c:
[ 
	{ div:["abs w35_"] }, // ami chan
	{ arg:["","",":v:users:usn"] },
	{ input:["g","optc","chvw0","%2","radio",""] }, 
	{ li:["x y02 cd"], c:			
	[
		{ div:["c w12"], c:[ { s:["c x y",":v:users:exten"] }, { s:["c x y",":v:users:usn"] } ] },
		{ s:["c x y g",""] },
		{ s:["c x y g",""] },	// vector
		{ s:["c x y",""] },		// cid2
		{ s:["d x y",""] },		// status-duration
		{ arg:["ts","",":v:users:last_break_ts"] }, 		// status-ts
		{ s:["d x y s",":v:users:last_break"] }, 		// status-text
		{ div:["e"] }
	]},
	{ div:[] }
]};

te["dash_agent_count"] = { s:["d y","%2"] };

// ----------------------------------------------------------------

rk["dash_inbound_metrics"] = ["in_calls","in_uniq","in_attempts","in_sla","in_avg_wait","in_avg_talk","in_avg_hold","in_occupied","in_available","disposition"];
re["dash_inbound_metrics"] = re["metrics"] ;
te["wall_inbound_args"] = { arg:["","vector","1"] };

te["dash_rpt_distf_r"] = { div:[], c:
[
        { input:["g","","distf","%0","radio","%9"] },
        { li:["opta x y tr cb","","%1"], ev:["_rpt_opt"] }
]};

te["dash_rpt_metric_r"] = { div:["c r15"], c:
[
        { input:["g","","rpt","%0","radio","%9"] },
        { li:["optt x03 y tc cd s"], ev:["_rpt_opt"], c:
        [
                { s:["c","%2"] },
                { s:["c l","%3"] },
                { div:["e"] }
        ]}
]};

te["dash_rpt_stats_r"] = { div:["c r15"], c:
[
        { input:["g","","rpt","stats","radio","1"] },
        { li:["optt x03 y tc cd s"], ev:["_rpt_opt"], c:
        [
                { s:["c","Stats"] },
                { s:["c l",""] },
                { div:["e"] }
        ]}
]};

te["dash_rpt_type_r"] = { div:[], c:
[
        { input:["g","","type","%0","radio","%9"] },
        { ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
        [
                { div:["c w02 t"], s:["opt",""] },
                { s:["c w10 y ","%1"] },
                { div:["e"] }
        ]}
]};

te["wall_rpt_vw"] = { c:
[
	{ pivot:[] },
	{ div:[], usummary:[] },
//	{ ufn:["wall_stats_ufn"] }
]};

te["wall_rpt"] = {  c:
[
       
        { form:["","vrpt"], c:
	[
		{ s:["g x15 y h3",null] },
		{ arg:["","type",null] }, 
		{ arg:["","stacked",null] },
		{ arg:["","xaxis",null] },
		{ arg:["","yaxis",null] },
		//{ arg:["","metrics",null] },
		{ input:["g","","rpt",null,"checkbox","1"] },
		{ u:[null] }
	]},
	{ div:["",null], urpt:[] } 
	
	
]};

te["wall_args_inbound"] = { c:[ { arg:["","vector","1"] } ] };

te["wall_calls"] = { div:["ma x15 y15"], c: // 
[
	
	{ div:[""], c:
        [
//          { p:["","wall_rpt_call"], wall_rpt:["Today's Call Traffic","bar","stacked","hangup_status_txt","h","call_count","wall_args_inbound","wall_rpt_vw-calls"] },
        ]},

	{ div:[""] }, // case stats here
	
	{ div:[""], s:["tt w80_",""], c:
	[
		{ div:["x y"], c:
		[
			{ div:["y07 h3 "], c:
			[
				{ s:["c x y","Counsellors Online"] },
				// { u:["dash_agent_count","users_ctx"] },
				// { s:["d x y","of"] },
				{ s:["d x y","0"] },
				{ div:["e"] }
			]},
			{ div:["x y02 b cd bb_"], c:
			[
				{ s:["c w03 x y","Ext."] },
				{ s:["c w11 x y","Name"] },
				{ s:["c w12 x y","Caller"] },
				{ s:["c w08 x y tr","Answered"] },
				{ s:["c w08 x y tr","Missed"] },
				{ s:["c w08 x y tr","Talk Time"] },
				{ s:["d w08 x y tr","Duration"] },
				{ s:["d w10 x y tr","Queue Status"] },
				{ div:["e"] }
			]},
			{ p:["","vagents"], c: // 
			[
				//{ s:["x y s gww" ,"No Agents Available"] },
				// { u:["dash_agent","users","","users"] }
			]},
		]},
		
		{ div:["x t15"], c:
		[
			{ div:["y07 h3 "], c:
			[
				{ s:["c x y","Calls in Queue"] },
				{ s:["d x y","0"] },
				{ div:["e"] }
			]},
			{ p:["mb","vqueued"] },
			{ div:["g y03"], c:
			[
				{ s:["c x y03 s","Queue Max Wait Time"] },
				{ s:["d x y03 s",":k:stats:in_max_wait:h"] },
				{ div:["e"] }
			]},
			{ div:["y02 b g"], c: // 
			[
				{ s:["c x y03 b  ","Inbound Calls"] },
				{ s:["d xx y03","0"] },
				{ div:["e"] }
			]},
			{ p:["mb","vinbound"] },
	
			{ div:["y02 s b g"], c:
			[
				{ s:["c x y03","Active Outbound Calls"] },
				{ s:["d x y03","0"] },
				{ div:["e"] }
			]},
			{ p:["mb g","voutbound"] }, // outbound	
		]},

		{ div:["x y cd g"], c:
		[
			{ s:["c x y","Queue Avg Wait Time"] },
			{ s:["d x y",":k:stats:in_avg_wait:h"] },
			{ div:["e"]}			
		]}
	]},
]},
	

te["wallboard"] = { c:
[
	{ div:[] },
	{ div:[], c:
	[
		{ arg:["","dash_period","today"] }
	]},
	{ div:["gww h100"], c:
	[
		{ div:[], c:[ { input:["g","","tabv","0","radio","1"] }, { p:["tabv mt","vt"], wall_calls:[] } ] },
		{ div:[], c:[ { input:["g","","tabv","1","radio"] }, { p:["tabv","vt"] } ] }, // wall my profile
	]}
]};

te["wallonly"] = { c:
[
        { div:["","vftab"], wallboard:[] },

        { div:["g"], c:
        [
                { arg:["user_cid","","---"] },
                { iframe:["","",VA_AMI_HOST] },
                //{ iframe:["","",VA_ATI_HOST] },
        ]},
]};


// --------------------------------------------------------------------

te["dash_case_priority_vw_r"] = { div:["w50 gws mb1 h03"], c: // 
[
	{ s:["abs w50",""], c:
	[
		{ div:[null] },
		{ div:[null] },
		{ div:[null] },
		{ div:["e"] }
	]},
	{ div:["abs w55 t08 cw"], c:
	[
		{ s:["c xx w48 cw",null] },
		{ s:["d xx cb",""] },
		{ div:["e"] }
	]}
]};

te["dash_case_priority_vw"] = { c:
[
	//{ div:["xx g"], c:
	//[
	//	{ div:["c w17 cd"], c:
	//	[
	//		{ s:["c x02 y02 w01 h01 bd32 gg",""] },
	//		{ s:["c x","Closed Cases"] },
	//		{ div:["e"] }
	//	]},
	//	{ div:["c w16 cd mr"], c:
	//	[
	//		{ s:["c x02 y02 w01 h01 bd32 go",""] },
	//		{ s:["c x","Ongoing Cases"] },
	//		{ div:["e"] }
	//	]},
	//	{ div:["c w16 cd mr"], c:
	//	[
	//		{ s:["c x02 y02 w01 h01 bd32 gbl",""] },
	//		{ s:["c x","Escalated Cases"] },
	//		{ div:["e"] }
	//	]},
	//				
	//	{ div:["e"] }
	//]},
	
	{ div:[] }, 
				
	{ div:["x"], c:  // 
	[
		{ dash_case_priority_vw_r:["c h02 y gg bb3_y","c h02 y gg bb3_p","c h02 y gg bb3_r","Closed Cases"] },
		{ dash_case_priority_vw_r:["c h02 y go bb3_y","c h02 y go bb3_p","c h02 y go bb3_r","Ongoing Cases"] },
		{ dash_case_priority_vw_r:["c h02 y gbl bb3_y","c h02 y gbl bb3_p","c h02 y gbl bb3_r","Escalated Cases"] },
	]},
				
	{ div:["x y"], c: 
	[
		{ ac:["c w11 ao mr1","","","xx y cb bd gws bb3_y",""], c:[ { s:["y tc n","Low Priority"] }, { s:["y b tc h","0"] }] },
		{ ac:["c w12 ao mr1","","","xx y cb bd gws bb3_p",""], c:[ { s:["y tc n","Medium Priority"] }, { s:["y b tc h","0"] }] },
		{ ac:["c w12 ao mr1","","","xx y cb bd gws bb3_r",""], c:[ { s:["y tc n","High Priority"] }, { s:["y b tc h","0"] }] },				
		{ ac:["c w12 ao","","","xx yy gb cw bd ",""], c:[ { s:["tc h3","Total"] }, { s:["y b tc h","0"] }] },
		{ div:["e"]}
	]}
]};		

te["dash_case_priority"] = { c:
[
	{ pivot:[] },
	{ dash_case_priority_vw:[] },
	{ ufn:["case_prio_chart"] }
]};

te["dash_rpt_line"] = { c:
[
	{ pivot:[] }, 
	{ div:["w55"], s:["",""], c:[ { canvas:["","","",""], uchart:[] } ] },
	{ div:["w55 yy"], s:["",""], utable:[] },
	{ div:["e"] }
]};

te["dash_rpt_pie"] = { c:
[
	{ pivot:[] }, 
	{ div:["c w22"], s:["",""], c:[ { canvas:["","","",""], uchart:[] } ] },
	{ div:["d ll"], s:["",""], utable:[] },
	{ div:["e"] }
]};

te["dash_rpt"] = { c: // dash_rpt:["Case Categories","bar","stacked","case_category_root_id","-","count","0","dash_rpt_pie-cases"]
[ 
	{ form:["yy","vrpt"], c:
	[
		{ s:["x15 y h3",null] },
		{ arg:["","type",null] }, 
		{ arg:["","stacked",null] },
		{ arg:["","xaxis",null] },
		{ arg:["","yaxis",null] },
		//{ arg:["","metrics",null] },
		{ input:["g","","rpt",null,"checkbox","1"] },
		{ arg:["","sortrpt","1"] }
	]},
	{ div:["xx yy",null], urpt:[] } 
]};

te["dash_src_r"] = { div:[], c:
[
	{ input:["g","","dash_src","%0","radio","%9"] },
	{ ac:["opti_","","_dash","x y gw mb cb ",""], c:
	[
		{ s:["x y tc","%1"] },
		{ div:["x y w03 ma"], s:["%2",""], c:[ { img:["","","%3","30"] } ] },
		{ s:["x y b tc h3 h02","%4"] }
	]}
]};

te["dash_gbv_r"] = { div:[], c:
[
	{ input:["g","","dash_gbv","%0","radio","%9"] },
	{ ac:["opti_","","_dash","x15 y cb","%1"] }
]};

te["dash_period_r"] = { div:[], c:
[
	{ input:["g","","dash_period","%0","radio","%9"] },
	{ ac:["opti_","","_dash","x15 y cb","%1"] }
]};

te["dash_view"] = { c:
[
	{ div:["c wp50"], s:["",""], c:
	[
		{ div:["x y gw mb h40","vc"], dash_rpt:["Case Categories","bar","stacked","cat_0","-","case_count","dash_rpt_pie-cases"] },	
		{ div:["x y gw mb","vc"], dash_rpt:["Case per Location","bar","stacked","reporter_location_0","-","case_count","dash_rpt_pie-cases"] },
	]},
	{ div:["c wp50"], s:["ml",""], c:
	[
		{ div:["x y gw mb h40","vc"], dash_rpt:["Daily Cases","line","","src","dt","case_count","dash_rpt_line-cases"] },		
		{ div:["x y gw mb","vc"], dash_rpt:["Case Status","bar","stacked","final_status,priority","-","case_count","dash_case_priority-cases"] },			
	]},
	{ div:["e"] }	
]}

te["dash"] = { c:
[
	{ div:[] },
	{ div:["abs w14_5","vdf"], c: // filter params
	[
		{ div:["gw mb"], c:
		[
			{ div:["ay","va"], ac:["","","_dd","x gw cb",""], c:
			[
				{ s:["c l y","::dash_period:0:1"] },
				{ div:["d w02 t04"], c:[ { div:["h02 w02 awb"] } ] },
				{ div:["e"] },
				{ s:["x b05 cd s",":d:dmy:3: "] }
			]},
			{ div:["dd w13 y ba gw bd","vdd"], c:
			[
				{ div:["c w13"], c:
				[
					{ uchk:["dash_period_r","%0","dash_period"] }
				]},
				{ div:["e"] }
			]},
		]},
		
		{ div:["gw mb"], c:
		[
			{ div:["ay","va"], ac:["","","_dd","x bd gw cb",""], c:
			[
				{ s:["c l y","::dash_gbv:1:1"] },
				{ div:["d w02 t04"], c:[ { div:["h02 w02 awb"] } ] },
				{ div:["e"] }
			]},
			{ div:["dd w13 y ba gw bd","vdd"], c:
			[
				{ uchk:["dash_gbv_r","%1","dash_gbv"] }
			]},
		]},							 

		{ uchk:["dash_src_r","%2","dash_src"] },
		
		{ arg:["","created_on","%3"] },
		{ arg:["","gbv_related","%4"] },
		{ arg:["","src","%5"] }
		
	]},
	{ div:["ml15"], dash_view:[] }
]};

// ------------------------------------------	

te["sbl"] = { div:[null], c: //
[
	{ input:["g","","sbl",null,"radio",null] },
	{ ac:["sbl ao",null,"_tab","yy cw",""], c: // todo: on hover show name
	[
		{ s:["micon l20 h2_ b tc",null] },
		{ s:[" tc s",null] },
		{ u:[null] }
	]},
]};

te["sbl_cat"] = { arg:["",".id","0"] };

te["sbl_case"] = { arg:["","_title","all_cases"] };

te["user_cid"] = { arg:["user_cid","","%7"] }; 

te["user_usn"] = { div:[], c:[ { s:["xx y cb b","%5"] }, { div:["e"] } ] }; 

te["toolbar_default"] = { div:["ma w15"], c:
[
	{ input:["g","","sbl_","1","radio","1"] },
	{ input:["g","","sbr_","1","radio"] },
	{ ac:["abs mtn45 ao t08 w15","","_activity_vw","xx bd gg cw",""], c:
	[
		{ s:["c y","Walk In"]},
		{ s:["d t03 h2 micon","directions_walk"] },
		{ div:["e"], c:[ { arg:["",".id","-1"] }, { arg:["","src","walkin"] }, { arg:["","src_address",""] } ] }
	]},
]};
			
te["main"] = { c: 
[
	{ div:["x y07 gw"], c: // 
	[
		{ div:["c "], s:["",""], c:
		[
			{ a:["c aa","","","/helpline/"], c:[ { img:["","",APP_LOGO, "48"] } ] },
			{ div:["e"] }
		]}, 		
			
		{ div:["d r10"], c:
		[
			{ input:["g","","rtab","0","radio"] },
			{ ac:["ll ay tab","","_mtabr","gw bd x y micon h2_ cb","history"] }				
		]},
		
		{ div:["d mr"], c:
		[
			{ input:["g","","rtab","1","radio"] },
			{ ac:["l15 ay tab","","_mtabr","gw bd cb",""], c:
			[
				{ p:["abs g","notif_count"], s:["ml2 x07 y02  h01_ tc gr cw bd16 s",""] },
				{ s:["x y micon h2_","notifications"] }				
			]},
		]},
		
		{ div:["d mr g"], c: // active chat (shown only when chat-activity is open)
		[
			{ input:["g","","rtab","2","radio"] },
			{ ac:["l15 ay rb","","_mtabr","gw bd cb",""], c:
			[
				{ p:["abs g","chat_count"], s:["ml2 x07 y02  h01_ tc gr cw bd16 s",""] },
				{ s:["x y micon h2_","chat"] }				
			]},
		]},
					
		{ div:["d w17 t01"], s:["abs w17 zzz",""], c:
		[
			{ div:["ay","va"], ac:["","","_dd","w17 bd gws_",""], c:
			[
				{ p:["","agent_status"], agent_status:["aoffline","gd bd h01 w01","cd","Connecting ...","",""] },									
				{ div:["e"], u:["user_cid","auth"] }
			]},
			{ div:["g w17","vdd"], s:["xx yy gw ba",""], c:
			[	
				{ div:[""], u:["user_usn","auth"] }, // 
				
				{ p:["","phone_status"], s:["xx y cd","Checking Phone Status ..."] },

				{ p:["","ati_status"] },
				
				{ p:["","aa_status"], ev:["boo"], c:[ { aa_status:["aa_none","","z"] } ] },
								
				{ p:["","joinq_status"] },
				
				{ div:["","va"], ac:["aa","myprofile-r_","_vp","xx y cb ",""], c:
				[
					{ s:["","My Profile"] },
					{ div:[] }
				]},
						
				{ div:["","va"], ac:["aa","logout-","_u","xx y cb ","Logout"], c:[ { arg:["","logout","1"] } ] },
			]},	

		]},

		{ p:["d xx","aa_status_ico"] },

		{ div:["e"] }
	]},
	
	{ div:["","vb"], toolbar_default:[] },
	
	{ div:["g"], c:  // 
	[
		{ div:["d w28"], s:["abs zz w28 gw mt",""], c:
		[
			{ div:[], c:
			[
				{ div:[], c:
				[
					{ input:["g","","ntabv","0","radio"] },
					{ p:["tabv","vt_activity"], u:["activity_lst","activities_ctx"] },
				]},
				{ div:[], c:
				[
					{ input:["g","","ntabv","1","radio"] },
					{ div:["tabv"], c:
					[
						{ div:["gw bb_ x y08"], c:
                                                [
                                                        { ac:["c w03 ay","","","x07 y h2 cb",""],  c:[ { s:["micon","search"] } ] },
                                                        { div:["c w21","txa"], c:[ { input:["w21 xx t08 b05 gw n","name_","","","text","","Enter Phone Number"] } ] },
                                                        { ac:["d w03 ay","","_dial","x07 y h2 cb",""],  c:[ { s:["micon","call"] } ] },
                                                        { div:["e"] },
                                                ]},
                                                { p:["","call_sessions"] }, // el.p.p.p.f.c1.c1
					]}
				]},
			]}
		]},
		
		{ div:["e"] } 
	]},

	{ p:["abs zz y op_ga g","vp"], ev:["_uvpd"] }, // popup window	
	
	{ p:["abs zzzz y op_ga g","vip"], ev:["_uvpd"] }, // incoming call popup	
		
	{ div:["h80 gb abs","vb"], s:["sb_",""], c: 
	[
		{ sbl:["","2","1","","speed","Dash","noop"] },
		
		{ sbl:["","3","","cases-cases","cases","Cases","sbl_case"] },
		
		{ sbl:["counsellor_ ","4","","calls-calls","call","Calls","noop"] },
		{ sbl:["supervisor_","4","","calls-calls","call","Calls","noop"] },
		{ sbl:["admin_","4","","calls-calls","call","Calls","noop"] },

		{ sbl:["counsellor_","5","","pmessages-pmessages","chat_bubble_outline","Other Channels","noop"] },
		{ sbl:["supervisor_","5","","pmessages-pmessages","chat_bubble_outline","Other Channels","noop"] },
		{ sbl:["admin_","5","","pmessages-pmessages","chat_bubble_outline","Other Channels","noop"] },
                { sbl:["media_","5","","pmessages-pmessages","chat_bubble_outline","Other Channels","noop"] },
				
		{ sbl:["supervisor_","6","","qas-qas","sentiment_satisfied","QA","noop"] },
		{ sbl:["admin_","6","","qas-qas","sentiment_satisfied","QA","noop"] },
		
		//sched
		//{ sbl:["supervisor_","7","","schedules-schedules","today","Schedule","noop"] },
		//{ sbl:["admin_","7","","schedules-schedules","today","Schedule","noop"] },
		
		//settings: campaigns, ivrs, users, categories
		//{ sbl:["supervisor_","8","","settings","settings","Settings","noop"] },
		//{ sbl:["admin_","8","","settings","settings","Settings","noop"] },
		{ sbl:["admin_","7","","categories-categories","account_tree","Categories","sbl_cat"] },
		{ sbl:["admin_","8","","users-users","manage_accounts","Users","noop"] },
		
		{ sbl:["counsellor_","10","","","dashboard","Wallboard","noop"] },
                { sbl:["supervisor_","10","","","dashboard","Wallboard","noop"] },
                { sbl:["admin_","10","","","dashboard","Wallboard","noop"] },


		{ sbl:["admin_","7","","contacts-contacts","import_contacts","Contacts","noop"] },
	]},

	{ div:["ml6"], c: // 
	[
		{ div:[], c:[ { div:["d w28"], s:["abs w27 x y zzz",""], c:
		[
			 // notifications
		]} ]},
		{ div:[], c:[ { input:["g","","mtv","1","radio"] }, { p:["tabv gw  mm","vfvwm"] } ] }, // on call & right sb vw
		{ div:[], c:[ { input:["g","","mtv","2","radio","1"] }, { p:["tabv mm","vftab"], u:["dash","dash"] } ] }, // wall board
		{ div:[], c:[ { input:["g","","mtv","3","radio"] }, { p:["tabv","vfvwm"] } ] }, // cases
		{ div:[], c:[ { input:["g","","mtv","4","radio"] }, { p:["tabv","vftab"] } ] }, // calls
		{ div:[], c:[ { input:["g","","mtv","5","radio"] }, { p:["tabv","vftab"] } ] }, // text (non-call) channels
		{ div:[], c:[ { input:["g","","mtv","6","radio"] }, { p:["tabv","vftab"] } ] }, // qa
		{ div:[], c:[ { input:["g","","mtv","7","radio"] }, { p:["tabv","vftab"] } ] }, // categories
		{ div:[], c:[ { input:["g","","mtv","8","radio"] }, { p:["tabv","vftab"] } ] }, // users
		{ div:[], c:[ { input:["g","","mtv","9","radio"] }, { p:["tabv","vftab"] } ] }, // 
		{ div:[], c:[ { input:["g","","mtv","10","radio"] }, { p:["tabv gw mm","vfvwm"], wallboard:[] } ] }, // wallboard


		
		{ div:["g"], c:
		[
			// { iframe:["","",VA_AMI_HOST] },
			// { iframe:["","",VA_ATI_HOST] },
		]},
	]}
]};

te["login"] = { div:["gw "], c:
[
	{ div:["loginbg"], s:["ma w100",""], c: 
	[
		{ div:["c t20"], c:
		[
			{ s:["x t20 b hhh","Hello,"] },
			{ s:["x b y hhh","Welcome back!"] }
		]},
		
		{ div:["d w32 mb12"], c:[ { div:["","ve"], c:
		[ 
		
			{ div:["ma w26 y40"], c:
			[ 
				//{ div:["c w13"], c:[ { img:["","","/helpline/images/coartofarms.jpg", "90"] } ] },
				{ div:["c w13 t15"], c:[ { img:["","",APP_LOGO, "100"] } ] },
				{ div:["e"] }
			]}, 
					
			{ p:["w26 x30 y30 gb bd cw","o"], c:
			[
				{ div:[""], c:
				[
					{ s:["hhh b cw","Log in"] }, 
					{ div:["e"] }
				]},
				{ div:["y"], c:
				[
					{ p:["","nb"], u:["nb","auth_nb"] },
					{ div:["e"] }
				]},
				{ div:["t"], c:
				[
					{ div:[], s:["x y02 cw","Username"] },
					{ div:["w26 gw bd"], c:[ { input:["w26 xx yy","","user","","text","","Enter Username"] } ] },
					//{ div:["e"] }
				]},
				{ div:["t15"], c:
				[
					{ div:[], s:["x y02 cw","Password"] },
					{ div:["w26 gw bd"], c:[ { input:["w26 xx yy","","pass","","password","","Enter Password"] } ] },
					//{ div:["e"] }
				]},
				{ div:["t"], c:
				[
					{ div:["c"], s:["x y02 cw","Remember me"] },
					{ div:["d"], s:["x y02 cw","Forgot Password"] },
					{ div:["e"] }
				]},
				{ div:["t40"], c:
				[
					{ div:[], ac:["ag btn","login-","_postj","xx yy go cb bd b h3 tc","Login","0"] },
					{ div:["e"] },
					]}
			]} 
		]} ]}
	]},
	// { div:["y h50"]}
]};

function _dash ()
{
	this.previousSibling.checked = true;
	var p = __(this,"vdf");
	var a = {args:"?", ".id":""};
	argv (p, a);
	url (p.parentNode, "dash", "dash", a.args);
}

function case_prio_chart (el, u, a, r, m)
{
	var status = {"":0, "0":0, "1":1, "2":0, "3":2 }
	var prio = {"":0, "0":0, "1":0, "2":1, "3":2 };
	var rr = ra["cases_pivot"];
	var j = null;
	var k = null;
	var m = 0;
	var rr_ = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
	for (var i=0; i<rr.length; i++)
	{
		j = status[rr[i][0]];
		k = prio[rr[i][1]];
		console.log ("[prio] ("+rr[i][0]+","+rr[i][1]+") ("+j+","+k+")")
		if (j==undefined) continue;
		if (k==undefined) continue;
		//console.log ("PRIO] "+j+","+k+" |"+ rr[i][0][0]+","+rr[i][1][0]);
		rr_[j][k] += 1*rr[i][2][0];
		rr_[3][k] += 1*rr[i][2][0];
	}
		
	for (var i=0; i<4; i++) rr_[i][3]=rr_[i][0]+rr_[i][1]+rr_[i][2];  // calc total
		
	for (var i=0; i<4; i++) el.childNodes[2].childNodes[i].firstChild.childNodes[1].innerHTML = rr_[3][i]; 
	
	console.log ("[PRIO] "+JSON.stringify (rr_)+" | "+m);
	
	for (var i=0; i<3; i++) 
	{
		el.childNodes[1].childNodes[i].childNodes[1].childNodes[1].innerHTML = rr_[i][3];
		var coll = el.childNodes[1].childNodes[i].firstChild.childNodes;
		for (j=0; j<3; j++) if (rr_[i][j]>0) 
		{
			var w = ((rr_[i][j]/rr_[3][3])*500)-1
			coll[j].style.width = w
			// console.log ("prio ("+i+","+j+") "+rr_[i][j]+" | "+w)
		}
	}
}

// -----------------------

function unloadphone (el, u, a, r, m)
{
	VOICEAPPS_UA.disconnect ();
}

function loadphone (el, u, a, r, m)
{
	var v = re["user_role"][ra["auth"][0][6]];
	if (v) document.getElementById ("vv").className = v[2];
	console.log ("loadphone: "+ra["auth"][0][7]+" | "+JSON.stringify (v));
	DetectDevices ();
	// VOICEAPPS_UA.connect (ra["auth"][0][7]);
}

function ami_wait (el, u, a, r, m)
{

}

function _phone_fmt (s)
{
	var a = 0;
	var n = s.length;
	for (var i=0; i<n; i++) 
	{
		var ch = s.substr (i,1);
		if (ch=="+" || ch=="0" || ch==" ") { a++; continue; }
		break;
	}
	if (n-a==9) return COUNTRY_CODE+s.substr (a,(n-a));
	return s.substr (a,(n-a));
}

function notifs ()
{
	var p = document.getElementById ("call_sessions");
	var el = document.getElementById ("notif_count");
	var n = 0;
	var cn = "none";
	if (p==null) return;
	n = CALL_COUNT+ATI_COUNT
	if (n>0) cn = "block"
	el.firstChild.innerHTML = n;
	el.style.display = cn;
}

function _mtabr ()
{
	var coll = document.getElementById ("vv").childNodes;
	var coll_ = coll[2].firstChild.firstChild.firstChild.childNodes; 
	var f = this.previousSibling.checked;
	if (f==true)
	{
		this.previousSibling.checked = false;
		coll[2].style.display = "none";
		coll[6].style.marginRight = "";	
		return
	}
	this.previousSibling.checked = true;
	coll_[this.previousSibling.value].firstChild.checked=true;
	coll[2].style.display = "block";
	coll[6].style.marginRight = "280px";
}

function rxmsg (ev)
{
        if (document.getElementById ("user_cid")==null) return;

        // console.error (ev.data)
        
        var o = JSON.parse (ev.data);

        if (o.ra_ts)
        {
                ra_ts = o.ra_ts;
                return;
        }

        if (o.ati)
        {
               ldati (o.ati)
               return;
        }

        if (o.peers)
        {
                re["peers"] = o.peers;
        }

        if (o.channels)
        {
                ldami (o.channels, o.c);
        }
}

window.addEventListener("message", rxmsg, false);

window.onresize = function ()
{
	// show_notifications (1);
}

window.onload = function ()
{
	ra_ts = 0; // (Date.now()/1000)-ra_ts; 

	Chart.defaults.global.responsive = false;
	Chart.defaults.global.maintainAspectRatio = false;
	Chart.defaults.global.elements.line.tension = 1;
	// Chart.defaults.global.elements.line.stepped = true;
	// Chart.defaults.global.elements.line.backgroundColor = "rgba(255,255,255,0)";
	Chart.defaults.global.elements.line.borderWidth = 0;
	Chart.defaults.global.elements.point.radius = 3;
	//Chart.defaults.global.elements.point.borderColor = "rgba(255,0,0,1)";
	Chart.defaults.global.elements.point.hitRadius = 10;
	// Chart.defaults.global.animation.duration = 0;

	var c;
	for (var n =0; n < 256; n++)
	{
        	c = n;
        	for (var k =0; k < 8; k++)
        	{
        	    c = ((c&1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));
        	}
        	CRC_TABLE[n] = c;
        }
        
	var p = document.getElementById ("vv"); 
	
	url (p, "login","","");
}

